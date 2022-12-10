#!/usr/bin/env python
import graphPlotter
import html

import urllib.request, json
url = "http://[316:c51a:62a3:8b9::2]/result.json"

# nodes indexed by coords
class NodeInfo:
  def __init__(self, ip, coords):
    self.ip = str(ip)
    self.label = str(ip).split(":")[-1]
    self.coords = str(coords)
    self.version = "unknown"
  def getCoordList(self):
    return self.coords.strip("[]").split(" ")
  def getParent(self):
    p = self.getCoordList()
    if len(p) > 0: p = p[:-1]
    return "[" + " ".join(p).strip() + "]"
  def getLink(self):
    c = self.getCoordList()
    return int(self.getCoordList()[-1].strip() or "0")

class LinkInfo:
  def __init__(self, a, b):
    self.a = a # NodeInfo
    self.b = b # NodeInfo

def generate_graph(time_limit=60*60*3):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())["yggnodes"]

    toAdd = []
    for key in data:
      if 'address' not in data[key] or 'coords' not in data[key]: continue
      ip = data[key]['address']
      coords = data[key]['coords']
      info = NodeInfo(ip, coords)
      try:
        if 'nodeinfo' in data[key]:
          if 'name' in data[key]['nodeinfo']:
            label = str(data[key]['nodeinfo']['name'])
            if len(label) <= 64:
              info.label = label
      except: pass
      info.label = html.escape(info.label)
      toAdd.append(info)

    nodes = dict()
    def addAncestors(info):
      coords = info.getParent()
      parent = NodeInfo("{} {}".format("?", coords), coords)
      parent.label = parent.ip
      nodes[parent.coords] = parent
      if parent.coords != parent.getParent(): addAncestors(parent)

    for info in toAdd: addAncestors(info)
    for info in toAdd: nodes[info.coords] = info

    sortedNodes = sorted(nodes.values(), key=(lambda x: x.getLink()))
    #for node in sortedNodes: print node.ip, node.coords, node.getParent(), node.getLink()

    edges = []
    for node in sortedNodes:
      if node.coords == node.getParent: continue
      edges.append(LinkInfo(node, nodes[node.getParent()]))

    print('%d nodes, %d edges' % (len(nodes), len(edges)))

    graph = graphPlotter.position_nodes(nodes, edges)
    js = graphPlotter.get_graph_json(graph)

    with open('api/static/graph.json', 'w') as f:
        f.write(js)

if __name__ == '__main__':
    generate_graph()
