#
# The Autobentifier
#
# Copyright (c) 2020, Arm Limited. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#

import networkx as nx
import re
import sys

class Node:
  """
  Simple Hashable node type representing a function in a call graph
  """
  def __init__(self, name, arg_pointer_cost=5, is_global_var=False, code_size=0, pertubation=0):
    self.name = re.sub("^Node_", "", name)
    self.code_size = code_size
    self.pertubation = pertubation 
    self.arg_pointer_cost = arg_pointer_cost
    self.is_global_var = is_global_var
  
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

  def __str__(self):
    return "Edge Weight: %f" % (self.weight)
  
  def __repr__(self):
    return "Edge Weight: %f" % (self.weight)

#dotfile = "demo.elf.c.cg.dot"
def get_call_graph_from_dotfile(dotfile):
  graph = nx.drawing.nx_pydot.read_dot(dotfile)
  in_degree = graph.in_degree()
  mg = nx.MultiDiGraph()
  for node in graph.nodes:
    mg.add_node(Node(node))
  # Edges dont have this sort of representation so we have to append additional attributes to each edge. May algorithms use weight as the default attribute so lets initialize one and update it later.
  for nfrom, nto, w in graph.edges:
    mg.add_edge(Node(nfrom), Node(nto), frequency=in_degree[nto], param_size=0, perturbation=0, weight=0)
  return mg

class CallGraph:
  def __init__(self):
    self.mg = nx.DiGraph()

  def read_dotfile(self, dotfile):
    graph = nx.drawing.nx_pydot.read_dot(dotfile)
    self.mg.graph = graph.graph
    in_degree = graph.in_degree()
    for node in graph.nodes:
      n = Node(node)
      self.mg.add_node(n.name, node_data=n, weight=1)
    # Edges dont have this sort of representation so we have to append additional attributes to each edge. May algorithms use weight as the default attribute so lets initialize one and update it later.
    for nfrom, nto, w in graph.edges:
      nodeFrom = Node(nfrom)
      nodeTo = Node(nto)
      if not self.mg.has_edge(nodeFrom, nodeTo):
        self.mg.add_edge(nodeFrom.name, nodeTo.name, edge_data=EdgeData(in_degree[nto]), weight=1)
      else:
        self.mg[nodeFrom.name][nodeTo.name]["edge_data"].frequency += in_degree[nto]

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
