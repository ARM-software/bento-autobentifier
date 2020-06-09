import autobentifier
from autobentifier.call_graph import CallGraph
from autobentifier.decompiler import Decompiler
from autobentifier.module_analyzer import ModuleAnalyzer
from glob import glob
from os import path
import logging
import networkx as nx
import nxmetis
# export PYTHONPATH=$PYTHONPATH:/usr/local/bin

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class InvalidAutoBentoParams(Exception):
  pass

class AutoBentifier:
  def __init__(self, object_file_names=[], obj_dirs=[], bb_dir="bb"):
    self.object_file_names = []
    self.intermediate_object_file_names = []

    print("Initializing AutoBentifier")
    if object_file_names:
      self.object_file_names = object_file_names
      for ob in object_file_names:
        self.intermediate_object_file_names.append(path.join(bb_dir, path.basename(ob)))
    elif obj_dirs:
      for obdir in obj_dirs:
        self.obj_file_names.extend(glob(path.join(obdir, "*.o"), recursive=True))
        for ob in object_files:
          self.intermediate_object_file_names.append(path.join(bb_dir, path.basename(ob)))
    else:
      logger.error("Called AutoBentifier without any target object config")
      raise InvalidAutoBentoParams 

    print("Decompiling object files")
    for of in self.object_file_names:
      decompiler = Decompiler(of, bb_dir)
      decompiler.decompile()

    print("Reconstructing Call Graph")
    # Build call graph from Dotfiles
    self.cg = CallGraph()
    for io in self.intermediate_object_file_names:
      self.cg.read_dotfile(io + ".c.cg.dot")

    print("Analyzing lifted modules")
    # Analyze the lifted modules
    self.ma = ModuleAnalyzer()
    for io in self.intermediate_object_file_names:
      self.ma.analyze(json_fname= io + ".config.json" , ll_fname=io + ".ll")

    # Update the vertices
    print("Updating vertices")
    removed = []
    for node in self.cg.graph.nodes:
      #import pdb; pdb.set_trace()
      if node not in self.ma.functions:
        logger.warning("[WARNING] Could not CG function %s in lifted code, will remove from Call Graph" % node)
        #self.cg.graph.remove_node(node)
        #removed.append(node)
        self.cg.graph.nodes[node]["node_data"].code_size = 8
        continue
      function = self.ma.functions[node]
      #print(function.name, function.size())
      self.cg.graph.nodes[node]["node_data"].code_size = function.size()
    for node in removed:
      print("Removing %s from CallGraph" % node)
      self.cg.graph.remove_node(node)

    # Update edges with the cost of moving data around
    print("Update function call edges with the cost of moving data around")
    for nfrom, nto in self.cg.graph.edges:
      arg_pointer_cost = self.cg.graph.nodes[nto]["node_data"].arg_pointer_cost
      if nto not in self.ma.functions:
        continue
      function = self.ma.functions[nto]
      param_cost = 0
      for param in function.parameters():
        param_cost += param.get_cost(param_cost)

      self.cg.graph[nfrom][nto]["edge_data"].param_size = param_cost
    print("Done, ready to partition")

  def partition(self, num_partitions=5):
    for node in self.cg.graph.nodes:
      w = self.cg.graph.nodes[node]["node_data"].weight
      self.cg.graph.nodes[node]["weight"] = int(w)
    for nfrom, nto in self.cg.graph.edges:
      w = self.cg.graph[nfrom][nto]["edge_data"].weight
      self.cg.graph[nfrom][nto]["weight"] = int(w)

    bgraph = nx.Graph(self.cg.graph)
    #import pdb; pdb.set_trace()
    parts = nxmetis.partition(bgraph, num_partitions)
    return parts



if __name__ == '__main__':
    pass
