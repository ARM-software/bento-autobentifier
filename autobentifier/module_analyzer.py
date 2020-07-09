from collections import defaultdict
from llvmlite import binding
import logging
import json
import re
import sys

## Normally would use LLVM to get this info, but that's a real PITA right now. Opt for simple json parser instead
binding.initialize()
binding.initialize_all_targets()
binding.initialize_all_asmprinters()
#with open("demo.elf.ll") as fp:
#  x = fp.read()
#xl = binding.parse_assembly(x)

logger = logging.getLogger("ModuleAnalyzer")

def basic_type_cost(mstr, pointer_cost):
  ptr_count = mstr.count("*")
  mstr = re.sub("\*", "", mstr)
  if "void" in mstr:
    return ptr_count * pointer_cost
  numbits = int(mstr[1:])
  numbytes = 1
  if numbits == 1:
    numbytes = 1
  else:
    numbytes = numbits / 8
  if ptr_count:
    return ptr_count * pointer_cost * numbytes
  else:
    return numbytes

def get_type_cost(t, pointer_cost=1):
  t_cost = 0
  ptr_cnt = 0
  if "[" in t:
    m = re.match(r"^\[(?P<arr_count>\d+)\s*x\s*(?P<type>\w\d+\**)\]", t)
    if not m:
      logger.error("Unexpected array type found %s" % t)
    arr_count = int(m.group('arr_count'))
    t_cost = arr_count * basic_type_cost(m.group('type'), pointer_cost)
  elif "(" in t: # Callback type
    # Assume this is all grouped as a pointer
    m = re.match(r"(?P<return_type>\w+\**)\s+\((?P<params>[a-zA-Z0-9, *]+)\)", t)
    if not m:
      logger.error("Unexpected function pointer type found %s" % t)
    t_cost += basic_type_cost(m.group('return_type'), pointer_cost)
    fp_params = m.group('params')
    for param in fp_params.split(','):
      t_cost += basic_type_cost(param.strip(), pointer_cost)
    t_cost *= pointer_cost

  else:
    t_cost = basic_type_cost(t, pointer_cost)
  
  return t_cost


class FunctionParam:
  def __init__(self, jsonStr):
    self.json = jsonStr

  @property
  def name(self):
    return self.json["name"]

  @property
  def realName(self):
    return self.json["realName"]

  @property
  def type(self):
    return self.json["type"]["llvmIr"]

  def get_cost(self, pointer_cost=1):
    t = self.type
    return get_type_cost(t, pointer_cost)

class Function:
  def __init__(self, jsonStr):
    self.json = jsonStr
    self.global_references = set()

  @property
  def startAddr(self):
    return int(self.json["startAddr"], 16)

  @property
  def endAddr(self):
    return int(self.json["endAddr"], 16)

  @property
  def name(self):
    return self.json["name"]
  
  def size(self):
    return self.endAddr - self.startAddr

  @property
  def returnType(self):
    return self.json["returnType"]["llvmIr"]
  
  def parameters(self):
    if 'parameters' in self.json:
      return [FunctionParam(x) for x in self.json["parameters"]]
    else:
      return []

  def add_global_reference(self, global_name):
    self.global_references.add(global_name)


class GlobalVar:
  def __init__(self, jsonStr):
    self.json = jsonStr
    self.constant = False

  @property
  def name(self):
    return self.json["name"]

  @property
  def realName(self):
    return self.json["realName"]

  @property
  def type(self):
    return self.json["type"]["llvmIr"]

  @property
  def storage(self):
    return self.json["storage"]
  
  def get_cost(self, pointer_cost=1):
    t = self.type
    return get_type_cost(t, pointer_cost)

class ModuleAnalyzer:
  def __init__(self):
    self.functions = defaultdict(None)
    self.globals = defaultdict(dict)

  def analyze(self, json_fname, ll_fname):
    with open(json_fname) as fp:
      js = json.load(fp)
      for g in js["globals"]:
        gname = g["name"]
        self.globals[gname] = GlobalVar(g)
      for function in js["functions"]:
        fname = function["name"]
        self.functions[fname] = Function(function)

    with open(ll_fname) as fp:
      x = fp.read()
      xl = binding.parse_assembly(x)
      # HACK HACK HACK HACK HACK HACK
      for g in xl.global_variables:
        if g.name and "constant" in str(g):
          #import pdb; pdb.set_trace()
          gg = self.globals[g.name].constant = True
          
      for fName in self.functions:
        try:
          f = xl.get_function(fName)
          #if f.is_declaration():
          #  continue
        except NameError:
          logger.info("Function %s not found in llvmlite" % fName)
          continue
        except:
          logger.warning("Unhandled exception occured in llvmlite.get_function")
          continue

        for b in f.blocks:
          # getting Globals is a real PITA, it's easier to parse the opcode
          for i in b.instructions:
            op_code = str(i)
            matches = re.findall(r"@(?P<global_ref>[_a-zA-Z]\w*)", op_code)
            if matches:
              for match in matches:
                if match in self.globals:
                  self.functions[fName].add_global_reference(match)
    for f in self.functions:
      if type(self.functions[f]) != Function:
        logger.warning("Encountered a invalid type in ModuleAnalyzer function list")


  def get_function(self, fName):
    if fName in self.functions:
      return self.functions[fName]
    else:
      return None
  def get_global(self, gName):
    if gName in self.globals:
      return self.globals[gName]
    else:
      return None


if __name__ == '__main__':
  m = ModuleAnalyzer
  m.analyze(sys.argv[1])


