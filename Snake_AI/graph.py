from typing import List
import random
import networkx as nx
import matplotlib.pyplot as plt
import json


class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: "Point") -> bool:
        return self.x == other.x and self.y == other.y

    def distanceTo(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def directionTo(self, other: "Point") -> "Point":
        return Point(other.x - self.x, other.y - self.y)

    def toTuple(self) -> tuple:
        return (self.x, self.y)


class Node(Point):
    neighours: list
    connected: list

    visited: bool

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.neighours = []
        self.connected = []
        self.visited = False


cols = 4
rows = 4

nodes = []

for i in range(cols):
    for j in range(rows):
        nodes.append(Node(i, j))

nodePosByName = {}
for i in range(len(nodes)):
    nodePosByName[f"Node_{i}"] = nodes[i].toTuple()

print(nodePosByName)


# with open("test.json", "w", encoding="UTF-8") as file:
#     json.dump(nodePosByName, file, indent=4)

edges = [
    ["Node_0", "Node_1"],
    ["Node_0", "Node_4"],
    ["Node_1", "Node_5"],
    ["Node_2", "Node_6"],
    ["Node_3", "Node_7"],
    ["Node_4", "Node_5"],
]

G = nx.Graph()
G.add_edges_from(edges)

nx.draw_networkx(G, pos=nodePosByName)

plt.show()
