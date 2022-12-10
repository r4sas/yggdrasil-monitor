import pygraphviz as pgv
import time
import json
import networkx as nx
from networkx.algorithms import centrality
import urllib.request

def position_nodes(nodes, edges):
    G = pgv.AGraph(strict=True, directed=False, size='10!')

    for n in nodes.values():
        G.add_node(n.ip, label=n.label, coords=n.coords)

    for e in edges:
        G.add_edge(e.a.ip, e.b.ip, len=1.0)

    G.layout(prog='neato', args='-Gepsilon=0.0001 -Gmaxiter=100000')

    return G

def compute_betweenness(G):
    ng = nx.Graph()
    for start in G.iternodes():
        others = G.neighbors(start)
        for other in others:
            ng.add_edge(start, other)

    c = centrality.betweenness_centrality(ng)

    for k, v in c.items():
        c[k] = v

    return c

def canonalize_ip(ip):
    return ':'.join( i.rjust(4, '0') for i in ip.split(':') )

def load_db():
    url = "http://[316:c51a:62a3:8b9::2]/result.json"
    f = urllib.request.urlopen(url)
    return dict(
        [
            (canonalize_ip(v[0]), v[1]) for v in
                [
                    l.split(None)[:2] for l in
                        json.loads(f.read())["yggnodes"].keys()
                ]
            if len(v) > 1
        ]
    )

def get_graph_json(G):
    max_neighbors = 1
    for n in G.iternodes():
        neighbors = len(G.neighbors(n))
        if neighbors > max_neighbors:
            max_neighbors = neighbors
    print('Max neighbors: %d' % max_neighbors)

    out_data = {
        'created': int(time.time()),
        'nodes': [],
        'edges': []
    }

    centralities = compute_betweenness(G)
    db = load_db()

    for n in G.iternodes():
        neighbor_ratio = len(G.neighbors(n)) / float(max_neighbors)
        pos = n.attr['pos'].split(',', 1)
        centrality = centralities.get(n.name, 0)
        size = 5*(1 + 1*centrality)
        name = db.get(canonalize_ip(n.name))
        # If label isn't the default value, set name to that instead
        if n.attr['label'] != n.name.split(':')[-1]: name = n.attr['label']

        out_data['nodes'].append({
            'id': n.name,
            'label': name if name else n.attr['label'],
            'name': name,
            'coords': n.attr['coords'],
            'x': float(pos[0]),
            'y': float(pos[1]),
            'color': _gradient_color(neighbor_ratio, [(100, 100, 100), (0, 0, 0)]),
            'size': size,
            'centrality': '%.4f' % centrality
        })

    for e in G.iteredges():
        out_data['edges'].append({
            'sourceID': e[0],
            'targetID': e[1]
        })

    return json.dumps(out_data)


def _gradient_color(ratio, colors):
    jump = 1.0 / (len(colors) - 1)
    gap_num = int(ratio / (jump + 0.0000001))

    a = colors[gap_num]
    b = colors[gap_num + 1]

    ratio = (ratio - gap_num * jump) * (len(colors) - 1)

    r = int(a[0] + (b[0] - a[0]) * ratio)
    g = int(a[1] + (b[1] - a[1]) * ratio)
    b = int(a[2] + (b[2] - a[2]) * ratio)

    return '#%02x%02x%02x' % (r, g, b)
