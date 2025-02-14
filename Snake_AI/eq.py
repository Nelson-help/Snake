import networkx as nx
import matplotlib.pyplot as plt

nodes = [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
]

positions = {}
edges = []
for i in range(len(nodes) - 1):
    positions[str(nodes[i])] = nodes[i]
    positions[str(nodes[i + 1])] = nodes[i + 1]
    edges.append((str(nodes[i]), str(nodes[i + 1])))

G = nx.Graph()
G.add_edges_from(edges)

nx.draw_networkx(G, pos=positions)

plt.show()
