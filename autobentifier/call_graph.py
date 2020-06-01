import networkx as nx
import sys

class Node:
  """
  Simple Hashable node type representing a function in a call graph
  """
  def __init__(self, name, arg_pointer_cost=5):
    self.name = name
    self.code_size = 0
    self.pertubation = 0
    self.arg_pointer_cost = arg_pointer_cost
  
  def __hash__(self):
    return self.name.__hash__()
  
  def __eq__(self, that):
    return self.__hash__() == that.__hash__()
  
  @property
  def weight(self):
    return self.code_size + self.pertubation
  
  def __str__(self):
    return "%s: %f" % (self.name, self.weight)
  
  def __repr__(self):
    return "%s: %f" % (self.name, self.weight)


#dotfile = "demo.elf.c.cg.dot"
def get_call_graph_from_dotfile(dotfile):
  graph = nx.MultiDiGraph(nx.drawing.nx_pydot.read_dot(dotfile))
  in_degree = graph.in_degree()
  mg = nx.MultiDiGraph()
  for node in graph.nodes:
    mg.add_node(Node(node))
  # Edges dont have this sort of representation so we have to append additional attributes to each edge. May algorithms use weight as the default attribute so lets initialize one and update it later.
  for nfrom, nto, w in graph.edges:
    mg.add_edge(Node(nfrom), Node(nto), frequency=in_degree[nto], param_size=0, perturbation=0, weight=0)
  return mg

if __name__ == '__main__':
  import pprint
  g = get_call_graph_from_dotfile(sys.argv[1])
  pprint.pprint(g.edges.data)
  #g[node_from][node_to][param_size] = 5
