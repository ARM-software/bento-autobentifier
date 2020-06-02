import networkx as nx
import re
import sys

class Node:
  """
  Simple Hashable node type representing a function in a call graph
  """
  def __init__(self, name, arg_pointer_cost=5):
    self.name = re.sub("^Node_", "", name)
    self.code_size = 0
    self.pertubation = 0
    self.arg_pointer_cost = arg_pointer_cost
  
  def __hash__(self):
    return self.name.__hash__()
  
  def __eq__(self, that):
    return self.name.__hash__() == that.__hash__()
  
  @property
  def weight(self):
    return self.code_size + self.pertubation
  
  def __str__(self):
    return "%s: %f" % (self.name, self.weight)
  
  def __repr__(self):
    return "%s: %f" % (self.name, self.weight)

class EdgeData:
  def __init__(self, freq):
    self.frequency = freq
    self.param_size = 0
    self.perturbation = 0

  @property
  def weight(self):
    return self.frequency + self.param_size + self.perturbation

#dotfile = "demo.elf.c.cg.dot"
#def get_call_graph_from_dotfile(dotfile):
#  graph = nx.MultiDiGraph(nx.drawing.nx_pydot.read_dot(dotfile))
#  in_degree = graph.in_degree()
#  mg = nx.MultiDiGraph()
#  for node in graph.nodes:
#    mg.add_node(Node(node))
#  # Edges dont have this sort of representation so we have to append additional attributes to each edge. May algorithms use weight as the default attribute so lets initialize one and update it later.
#  for nfrom, nto, w in graph.edges:
#    mg.add_edge(Node(nfrom), Node(nto), frequency=in_degree[nto], param_size=0, perturbation=0, weight=0)
#  return mg

class CallGraph:
  def __init__(self):
    self.mg = nx.Graph()

  def read_dotfile(self, dotfile):
    graph = nx.MultiDiGraph(nx.drawing.nx_pydot.read_dot(dotfile))
    in_degree = graph.in_degree()
    for node in graph.nodes:
      n = Node(node)
      self.mg.add_node(n.name, node_data=n, weight=0)
    # Edges dont have this sort of representation so we have to append additional attributes to each edge. May algorithms use weight as the default attribute so lets initialize one and update it later.
    for nfrom, nto, w in graph.edges:
      if not self.mg.has_edge(Node(nfrom), Node(nto)):
        self.mg.add_edge(Node(nfrom), Node(nto), edge_data=EdgeData(in_degree[nto]), weight=0)
      else:
        self.mg[Node(nfrom)][Node(nto)]["edge_data"].frequency += in_degree[nto]

  @property
  def graph(self):
    return self.mg

if __name__ == '__main__':
  import pprint
  cg = CallGraph()
  cg.read_dotfile(sys.argv[1])
  g = cg.graph
  pprint.pprint(g.edges.data)
  #g[node_from][node_to][param_size] = 5
