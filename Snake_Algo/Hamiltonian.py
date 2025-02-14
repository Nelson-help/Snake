from typing import List
import random


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

    cycleNo: int

    shortestDist: int # calculating shortcut path

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.neighours = []
        self.connected = []
        self.visited = False

    def SetNeighbors(self, allNodes: List["Node"]) -> None:
        self.neighbors = []
        for node in allNodes:
            if self.distanceTo(node) == 1:
                self.neighbors.append(node)

    def SetSpanningTreeEdges(self, allEdges: List["Edge"]) -> None:
        self.connected = []
        for edge in allEdges:
            if edge.Contains(self):
                self.connected.append(edge.GetOtherNode(self))


class Edge:
    node1: Node
    node2: Node

    def __init__(self, node1: Node, node2: Node) -> None:
        self.node1 = node1
        self.node2 = node2

    def __eq__(self, other: "Edge") -> bool:
        return self.Contains(other.node1) and self.Contains(other.node2)

    def Contains(self, other: Node) -> bool:
        return (self.node1 == other) or (self.node2 == other)

    def GetOtherNode(self, other: Node) -> Node:
        if (other == self.node1):
            return self.node2
        if (other == self.node2):
            return self.node1
        return Node(-1, -1)


class Cycle:
    cycleNodes: List[Node]

    def __init__(self, cols: int, rows: int) -> None:
        self.GenerateCycle(cols, rows)

    def GetNodeAt(self, x: int, y: int) -> Node:
        for node in self.cycleNodes:
            if node.x == x and node.y == y:
                return node
        return Node(-1, -1)

    def GetCycleDist(self, nodeNoA: int, nodeNoB: int) -> int:
        if nodeNoB < nodeNoA:
            return nodeNoB + len(self.cycle) - nodeNoA
        else:
            return nodeNoB - nodeNoA + 1

    def GetNodeNo(self, p: Point) -> int:
        for node in self.cycle:
            if (node == p):
                return node.cycleNo
        return -1

    @staticmethod
    def CreateSpanningTree(cols: int, rows: int) -> List[Node]:
        spanningTreeNodes = []
        for i in range(cols // 2):
            for j in range(rows // 2):
                spanningTreeNodes.append(Node(i, j))

        for node in spanningTreeNodes:
            node.SetNeighbors(spanningTreeNodes)

        currentNode = random.choice(spanningTreeNodes)

        spanningTree = [Edge(currentNode, currentNode.neighbors[0])]

        currentNode.visited = True
        currentNode.neighbors[0].visited = True
        visitedNodes = [currentNode, currentNode.neighbors[0]]

        while (len(visitedNodes) < len(spanningTreeNodes)):
            for node in visitedNodes:
                nextNode = None
                for neighbor in node.neighbors:
                    if (neighbor.visited):
                        continue
                    nextNode = neighbor
                    break
                if (not nextNode):
                    continue  # nextNode != Node, nextNode.visited = False
                nextNode.visited = True
                visitedNodes.append(nextNode)
                spanningTree.append(Edge(node, nextNode))
                break

        for node in spanningTreeNodes:
            node.SetSpanningTreeEdges(spanningTree)

        return spanningTreeNodes

    def GenerateCycle(self, cols: int, rows: int) -> None:
        spanningTreeNodes = self.CreateSpanningTree(cols, rows)
        self.cycleNodes = []

        for i in range(cols):
            for j in range(rows):
                self.cycleNodes.append(Node(i, j))

        for node in self.cycleNodes:
            node.SetNeighbors(self.cycleNodes)

        def connectScaledAdjacent(x1, y1, x2, y2):
            if (x1 < 0 or x1 >= cols or y1 < 0 or y1 >= rows):
                return
            if (x2 < 0 or x2 >= cols or y2 < 0 or y2 >= rows):
                return
            node1 = self.GetNodeAt(x1, y1)
            node2 = self.GetNodeAt(x2, y2)
            node1.connected.append(node2)
            node2.connected.append(node1)

        for node in spanningTreeNodes:
            for connectedNode in node.connected:
                direction = node.directionTo(connectedNode)
                scaledX = node.x * 2
                scaledY = node.y * 2
                if (direction.x == 1):
                    connectScaledAdjacent(scaledX + 1, scaledY,
                                          scaledX + 2, scaledY)
                    connectScaledAdjacent(scaledX + 1, scaledY + 1,
                                          scaledX + 2, scaledY + 1)
                if (direction.y == 1):
                    connectScaledAdjacent(scaledX, scaledY + 1,
                                          scaledX, scaledY + 2)
                    connectScaledAdjacent(scaledX + 1, scaledY + 1,
                                          scaledX + 1, scaledY + 2)

        # Stage 2
        singleConnectedNodes = []
        for node in self.cycleNodes:
            if len(node.connected) == 1:
                singleConnectedNodes.append(node)

        for NodeA in singleConnectedNodes:
            direction = NodeA.directionTo(NodeA.connected[0])
            posX = NodeA.x - direction.x
            posY = NodeA.y - direction.y
            if (posX < 0 or posX >= cols or posY < 0 or posY >= rows):
                continue
            NodeB = self.GetNodeAt(posX, posY)
            if (NodeA not in NodeB.connected):
                NodeB.connected.append(NodeA)
            if (NodeB not in NodeA.connected):
                NodeA.connected.append(NodeB)

        # Stage 3
        singleConnectedNodes = []
        for node in self.cycleNodes:
            if len(node.connected) != 1:
                continue
            singleConnectedNodes.append(node)

        for NodeA in singleConnectedNodes:
            for NodeB in singleConnectedNodes:
                if (NodeA.distanceTo(NodeB) != 1):
                    continue
                if (NodeA.x//2 != NodeB.x//2):
                    continue
                if (NodeA.y//2 != NodeB.y//2):
                    continue
                if (NodeA not in NodeB.connected):
                    NodeB.connected.append(NodeA)
                if (NodeB not in NodeA.connected):
                    NodeA.connected.append(NodeB)

        # Construct Cycle
        self.cycle = [random.choice(self.cycleNodes)]
        prv = self.cycle[0]
        crt = self.cycle[0].connected[0]
        nxt = None
        while (crt != self.cycle[0]):
            nxt = crt.connected[0]
            if (nxt == prv):
                nxt = crt.connected[1]
            self.cycle.append(crt)
            prv = crt
            crt = nxt
        for i in range(len(self.cycle)):
            self.cycle[i].cycleNo = i

# The less the preserveDist, the higher chance of dieing


class ShortCutPath:
    def __init__(self, path) -> None:
        self.path = path
        self.cost = len(self.path)

    def GetCurrentNode(self) -> Node:
        return self.path[len(self.path) - 1]

    def SetCostTo(self, target: Point) -> None:
        self.cost = len(self.path) + abs(self.GetCurrentNode().x - target.x)\
                        + abs(self.GetCurrentNode().y - target.y)

    def __gt__(self, other: "ShortCutPath") -> bool:
        if self.cost == other.cost:
            return len(self.path) > len(other.path)
        else:
            return self.cost > other.cost

    def GetEndTailPosition(self, body: List[Point], preserveDist: int) -> Point:
        snakeFollowPath = body.copy() + self.path
        if len(snakeFollowPath) < len(body) + preserveDist:
            return snakeFollowPath[0]
        else:
            return snakeFollowPath[len(snakeFollowPath) - len(body) - preserveDist]

    def GetStepNo(self, p: Point) -> int:
        for i in range(len(self.path)):
            if self.path[i] == p:
                return i
        return -1


# myCycle = Cycle(6, 6)

# positions = {}
# edges = []

# for node in myCycle.cycleNodes:
#     for connected_node in node.connected:
#         positions[str(node.toTuple())] = node.toTuple()
#         positions[str(connected_node.toTuple())] = connected_node.toTuple()
#         edges.append((str(node.toTuple()),
#                       str(connected_node.toTuple())))

# G = nx.Graph()
# G.add_edges_from(edges)

# nx.draw_networkx(G, pos=positions)

# plt.show()
