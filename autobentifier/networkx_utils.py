#
# The Autobentifier
#
# Copyright (c) 2020, Arm Limited. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#

import pydot
from collections import defaultdict
import networkx as nx

def make_str(thing):
  return  "%s" % thing

def get_entrypoints(graph, partitions):
  cost, modules = partitions
  mod_dict = defaultdict(lambda: int(-1))
  ep_dict  = defaultdict(bool)

  # Node -> module id map
  for i, module in enumerate(modules):
    for n in module:
      mod_dict[n] = i
  for u, v in graph.edges:
    if mod_dict[u] != mod_dict[v]:
      ep_dict[v] = True
  return ep_dict


def to_pydot(N, modules):
  """Returns a pydot graph from a NetworkX graph N.

  Parameters
  ----------
  N : NetworkX graph
    A graph created with NetworkX

  Examples
  --------
  >>> K5 = nx.complete_graph(5)
  >>> P = nx.nx_pydot.to_pydot(K5)

  Notes
  -----

  """
  #import pydot

  # set Graphviz graph type
  if N.is_directed():
    graph_type = 'digraph'
  else:
    graph_type = 'graph'
  strict = nx.number_of_selfloops(N) == 0 and not N.is_multigraph()

  name = "Call graph"
  graph_defaults = {} #N.graph.get('graph', {})
  if name == '':
    P = pydot.Dot('', graph_type=graph_type, strict=strict,
            **graph_defaults)
  else:
    P = pydot.Dot('"%s"' % name, graph_type=graph_type, strict=strict,
            **graph_defaults)
  #try:
  #  P.set_node_defaults(**N.graph['node'])
  #except KeyError:
  #  pass
  #try:
  #  P.set_edge_defaults(**N.graph['edge'])
  #except KeyError:
  #  pass

  #for n, nodedata in N.nodes(data=True):
  #  str_nodedata = dict((k, make_str(v)) for k, v in nodedata.items())
  #  p = pydot.Node(make_str(n), **str_nodedata)
  #  P.add_node(p)
  cost, module_list = modules
  entrypoints = get_entrypoints(N, modules)

  for module_num, m in enumerate(module_list):
    mName = "bb_%d" % module_num
    ep_cluster = pydot.Cluster(mName, label=mName, color="blue3", fontcolor="blue3")
    mName = "%s_internal" % mName
    cluster = pydot.Cluster(mName, label=mName, color="cornsilk1", fontcolor="cornsilk1")
    for n in m:
      if n in entrypoints:
        node = pydot.Node(n, style="filled", fillcolor="darkolivegreen3")
        ep_cluster.add_node(node)
      else:
        node = pydot.Node(n, style="filled", fillcolor="azure")
        cluster.add_node(node)
    ep_cluster.add_subgraph(cluster)
    P.add_subgraph(ep_cluster)

  if N.is_multigraph():
    for u, v, key, edgedata in N.edges(data=True, keys=True):
      str_edgedata = dict((k, make_str(v)) for k, v in edgedata.items()
                if k != 'key')
      edge = pydot.Edge(make_str(u), make_str(v),
                key=make_str(key), **str_edgedata)
      P.add_edge(edge)

  else:
    for u, v, edgedata in N.edges(data=True):
      str_edgedata = dict((k, make_str(v)) for k, v in edgedata.items())
      edge = pydot.Edge(make_str(u), make_str(v), **str_edgedata)
      P.add_edge(edge)
  return P


def write_dot(path, G, modules):
  """Write NetworkX graph G to Graphviz dot format on path.

  Path can be a string or a file handle.
  """
  P = to_pydot(G, modules)
  with open(path, "w") as fp:
    fp.write(P.to_string())
  return
