from Constants import (
    FPS,
    WIDTH,
    HEIGHT,
    BOARD_COLS,
    BOARD_ROWS,
    BLOCK_SIZE,
    BORDER_WIDTH,
    SNAKE_INITIAL_LENGTH,
    SNAKE_COLOR,
    APPLE_COLOR,
    BG_COLOR,
)


from Hamiltonian import Point, Node, Cycle, ShortCutPath

import random
import pygame

pygame.init()

FONT = pygame.font.SysFont("georgia", 200)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()


class Apple(Point):
    def __init__(self, snake: "Snake"):
        self.randomize(snake)

    def randomize(self, snake: "Snake"):
        available = []
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if (not snake.pointInSnake(Point(x, y))):
                    available.append(Point(x, y))
        point = random.choice(available)
        self.x = point.x
        self.y = point.y

    def draw(self):
        size = int((BLOCK_SIZE - 2 * BORDER_WIDTH) / 3)
        pygame.draw.rect(WINDOW, APPLE_COLOR, pygame.Rect(
            self.x * BLOCK_SIZE + BORDER_WIDTH + size,
            self.y * BLOCK_SIZE + BORDER_WIDTH,
            size,
            size
        ))
        pygame.draw.rect(WINDOW, APPLE_COLOR, pygame.Rect(
            self.x * BLOCK_SIZE + BORDER_WIDTH,
            self.y * BLOCK_SIZE + BORDER_WIDTH + size,
            size,
            size
        ))
        pygame.draw.rect(WINDOW, APPLE_COLOR, pygame.Rect(
            self.x * BLOCK_SIZE + BORDER_WIDTH + 2 * size,
            self.y * BLOCK_SIZE + BORDER_WIDTH + size,
            size,
            size
        ))
        pygame.draw.rect(WINDOW, APPLE_COLOR, pygame.Rect(
            self.x * BLOCK_SIZE + BORDER_WIDTH + size,
            self.y * BLOCK_SIZE + BORDER_WIDTH + 2 * size,
            size,
            size
        ))


class Snake(Point):
    def __init__(self):
        self.respawn()

    def respawn(self):
        self.hamiltonianCycle = Cycle(BOARD_COLS, BOARD_ROWS)
        self.cuttingPath = None
        self.score = 0
        self.addCount = 0
        self.vel = Point(1, 0)
        self.body = []
        self.x = int(BOARD_COLS/2)
        self.y = int(BOARD_ROWS/2)
        for i in range(1, SNAKE_INITIAL_LENGTH):
            self.body.append(Point(self.x - (SNAKE_INITIAL_LENGTH - i),
                                   self.y))
        self.apple = Apple(self)

    def pointInSnake(self, p: Point):
        return self == p or self.pointInBody(p)

    def pointInBody(self, p: Point):
        for block in self.body:
            if (block == p):
                return True
        return False

    def update(self):
        if self.checkCollision(): return self.respawn()

        if not self.cuttingPath:
            self.cuttingPath = self.findCuttingPath(self, self.apple)

        nextPos = self.hamiltonianCycle.cycle[
            (self.hamiltonianCycle.GetNodeNo(self) + 1) %
            (BOARD_ROWS * BOARD_COLS)
        ]
        self.vel.x = nextPos.x - self.x
        self.vel.y = nextPos.y - self.y

        if self.cuttingPath:
            nextStepNo = self.cuttingPath.GetStepNo(self) + 1
            if nextStepNo < len(self.cuttingPath.path):
                nextPos = self.cuttingPath.path[nextStepNo]
                self.vel.x = nextPos.x - self.x
                self.vel.y = nextPos.y - self.y

        if self.addCount > 0: self.addCount -= 1
        else: self.body.pop(0)

        self.body.append(Point(self.x, self.y))
        self.x += self.vel.x
        self.y += self.vel.y

    def findCuttingPath(self, start: Point, end: Point):
        availableNodes = []
        begNodeNo = self.hamiltonianCycle.GetNodeNo(start)
        endNodeNo = self.hamiltonianCycle.GetNodeNo(end)
        nodeCount = self.hamiltonianCycle.GetCycleDist(begNodeNo, endNodeNo)
        for i in range(nodeCount):
            node = self.hamiltonianCycle.cycle[(begNodeNo + i) % len(self.hamiltonianCycle.cycle)]
            availableNodes.append(Node(node.x, node.y))
        
        for node in availableNodes: node.SetNeighbors(availableNodes)

        winningPath = None
        currentPath = ShortCutPath([availableNodes[0], ])
        currentPath.SetCostTo(end)

        openPaths = [currentPath, ]

        while(len(openPaths) > 0):
            currentPath = openPaths.pop(0)

            if winningPath and len(currentPath.path) > len(winningPath.path):
                continue

            currentNode = currentPath.GetCurrentNode()

            if currentNode == end: 
                if not winningPath or len(currentPath.path) < len(winningPath.path):
                    winningPath = currentPath
                continue

            if not currentNode.visited or len(currentPath.path) < currentNode.shortestDist:
                currentNode.visited = True
                currentNode.shortestDist = len(currentPath.path)

                for node in currentNode.neighbors:
                    if self.pointInBody(node): continue
                    skipCount = self.hamiltonianCycle.GetCycleDist(
                        self.hamiltonianCycle.GetNodeNo(currentNode),
                        self.hamiltonianCycle.GetNodeNo(node),
                    )

                    distToTail = self.hamiltonianCycle.GetCycleDist(
                        self.hamiltonianCycle.GetNodeNo(currentNode),
                        self.hamiltonianCycle.GetNodeNo(currentPath.GetEndTailPosition(self.body, self.addCount + 4))
                    )

                    if skipCount == distToTail or distToTail < len(self.body)/10: continue
                    if not node.visited or len(currentPath.path) + 1< node.shortestDist:
                        extendedPath = ShortCutPath(currentPath.path.copy())
                        extendedPath.path.append(node)
                        openPaths.append(extendedPath)
                        openPaths.sort(key=lambda p: p.cost)
                        
            return winningPath


    def draw(self):
        self.apple.draw()
        pygame.draw.rect(WINDOW, SNAKE_COLOR, pygame.Rect(
            self.x * BLOCK_SIZE + BORDER_WIDTH,
            self.y * BLOCK_SIZE + BORDER_WIDTH,
            BLOCK_SIZE - 2 * BORDER_WIDTH,
            BLOCK_SIZE - 2 * BORDER_WIDTH
        ))
        for index in range(len(self.body)):
            current = self.body[index]
            if (index + 1 == len(self.body)):
                next = Point(self.x, self.y)
            else:
                next = self.body[index + 1]
            pygame.draw.rect(WINDOW, SNAKE_COLOR, pygame.Rect(
                current.x * BLOCK_SIZE + BORDER_WIDTH,
                current.y * BLOCK_SIZE + BORDER_WIDTH,
                BLOCK_SIZE - 2 * BORDER_WIDTH,
                BLOCK_SIZE - 2 * BORDER_WIDTH
            ))
            pygame.draw.rect(WINDOW, SNAKE_COLOR, pygame.Rect(
                (current.x + next.x)/2 * BLOCK_SIZE + BORDER_WIDTH,
                (current.y + next.y)/2 * BLOCK_SIZE + BORDER_WIDTH,
                BLOCK_SIZE - 2 * BORDER_WIDTH,
                BLOCK_SIZE - 2 * BORDER_WIDTH
            ))
        headCenter = Point(int((self.x + 0.5)*BLOCK_SIZE), int((
            self.y + 0.5)*BLOCK_SIZE))
        delta = Point(int(self.vel.x * BLOCK_SIZE/4),
                      int(self.vel.y * BLOCK_SIZE/4))
        eyeRadius = BLOCK_SIZE/16
        pygame.draw.circle(WINDOW, (0, 0, 0), (
            headCenter.x + delta.x/2 - delta.y,
            headCenter.y - delta.x + delta.y/2),
            eyeRadius)
        pygame.draw.circle(WINDOW, (0, 0, 0), (
            headCenter.x + delta.x/2 + delta.y,
            headCenter.y + delta.x + delta.y/2),
            eyeRadius)
        pygame.draw.line(WINDOW, (0, 0, 0), (
                    headCenter.x - delta.x/2 - delta.y,
                    headCenter.y - delta.y/2 - delta.x,
                ), (
                    headCenter.x - delta.x/2 + delta.y,
                    headCenter.y - delta.y/2 + delta.x,
                ), int(eyeRadius))

    def checkCollision(self):
        if (BOARD_ROWS * BOARD_COLS <= len(self.body) + 1): return True
        if self.x >= BOARD_COLS or self.x < 0: return True
        if self.y >= BOARD_ROWS or self.y < 0: return True
        if self.pointInBody(Point(self.x, self.y)): return True
        if (self == self.apple):
            self.addCount += 1
            self.score += 1
            self.apple.randomize(self)
            self.cuttingPath = None
        return False


def main():
    snake = Snake()

    while (True):
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return pygame.quit()

        WINDOW.fill(BG_COLOR)

        label = FONT.render(f"{snake.score}", False, (255, 255, 255))
        w, h = label.get_size()
        WINDOW.blit(label, (int(WIDTH - w) / 2, int(HEIGHT - h) / 2))
        snake.draw()
        snake.update()

        pygame.display.update()


if __name__ == "__main__":
    main()
