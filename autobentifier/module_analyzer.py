from collections import defaultdict
from llvmlite import binding
import json
import sys

## Normally would use LLVM to get this info, but that's a real PITA right now. Opt for simple json parser instead
#binding.initialize()
#binding.initialize_all_targets()
#binding.initialize_all_asmprinters()
#with open("demo.elf.ll") as fp:
#    x = fp.read()
#xl = binding.parse_assembly(x)

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


class Function:
    def __init__(self, jsonStr):
        self.json = jsonStr

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
        return [FunctionParam(x) for x in self.json["parameters"]]


class GlobalVar:
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

    @property
    def storage(self):
        return self.json["storage"]

class ModuleAnalyzer:
    def __init__(self):
        self.functions = defaultdict(dict)
        self.globals = defaultdict(dict)

    def analyze(self, fname):
        with open(fname) as fp:
            js = json.load(fp)
            for function in js["functions"]:
                fname = function["name"]
                self.functions[fname] = Function(function)
            for g in js["globals"]:
                gname = g["name"]
                self.globals = GlobalVar(g)


if __name__ == '__main__':
    m = ModuleAnalyzer
    m.analyze(sys.argv[1])


