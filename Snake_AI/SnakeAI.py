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
    DEAD_REWARD,
    GROW_REWARD,
    NONE_REWARD    
)


from Utils import Point
from model import QBrain

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
        self.round = 0 # No. games
        # If saved => read else: 0
        self.bestScore = 0
        self.brain = QBrain()
        self.respawn()

    def respawn(self):
        self.round += 1
        # self.moves = 0 # Moved steps
        self.score = 0
        self.addCount = 0
        self.vel = Point(1, 0)
        self.body = []
        self.x = int(BOARD_COLS/2)
        self.y = int(BOARD_ROWS/2)
        for i in range(1, SNAKE_INITIAL_LENGTH):
            self.body.append(Point(self.x - (SNAKE_INITIAL_LENGTH - i), self.y))
        self.apple = Apple(self)

    def pointInSnake(self, p: Point):
        return self == p or self.pointInBody(p)

    def pointInBody(self, p: Point):
        for block in self.body:
            if (block == p): return True
        return False
    
    def turn(self, action):
        if action[0]: #Straight
            return
        
        if action[1]:
            self.vel = Point(self.vel.y, -self.vel.x) # Left
            return
        
        if action[2]:
            self.vel = Point(-self.vel.y, self.vel.x) # Right
            return
    
    def state(self):
        deadIfGoU= self.pointInBody(Point(self.x, self.y - 1)) or self.y - 1 < 0 # Booleans for death
        deadIfGoD = self.pointInBody(Point(self.x, self.y + 1)) or self.y + 1 >= BOARD_ROWS 
        deadIfGoL = self.pointInBody(Point(self.x - 1, self.y)) or self.x - 1 < 0
        deadIfGoR = self.pointInBody(Point(self.x + 1, self.y)) or self.x + 1 >= BOARD_ROWS

        goingU= self.vel.y == -1 # Vel is from object's perspective
        goingD = self.vel.y == 1
        goingL = self.vel.x == -1
        goingR = self.vel.x == 1

        data = [ # Input_counts
            # 1. Dead if go striaght
            (
                goingU and deadIfGoU
            ) or (
                goingD and deadIfGoD
            ) or (
                goingL and deadIfGoL
            ) or (
                goingR and deadIfGoR
            ),
            # 2. Dead if turn left from perspective
            (
                goingU and deadIfGoL
            ) or (
                goingD and deadIfGoR
            ) or (
                goingL and deadIfGoD
            ) or (
                goingR and deadIfGoU
            ),
            # 3. Dead if turn right from perspective
            (
                goingU and deadIfGoR
            ) or (
                goingD and deadIfGoL
            ) or (
                goingL and deadIfGoU
            ) or (
                goingR and deadIfGoD
            ),
            # 4 ~ 7 Am I going ? dir
            goingU, 
            goingD,
            goingL,
            goingR,
            # 8 ~ 11 From my perspective where is the apple
            self.apple.x < self.x,
            self.apple.x > self.x,
            self.apple.y < self.y,
            self.apple.y > self.y,
        ]

        return data

    def update(self):
        # Think action
        useRandom = random.randint(0, 200) < 100 - self.round # As I play more, the frequency of useRandom goes down
        nowState = self.state() # Current state
        action = self.brain.think(nowState, useRandom)

        # Take Action
        self.turn(action) 

        # Move
        if self.addCount > 0: self.addCount -= 1 # Once added, remove 1 from addCount (addCount is the blocks still needed to add)
        else: self.body.pop(0) # Delete tail after movement to look like moving

        self.body.append(Point(self.x, self.y)) # Duplicate head as part of body
        self.x += self.vel.x # Remake moved head
        self.y += self.vel.y

        # Check result
        reward = self.checkCollision()

        newState = self.state()

        self.brain.memorize(nowState, action, reward, newState, reward == DEAD_REWARD) # Important = Dead

        if reward == DEAD_REWARD:
            if self.score > self.bestScore: # Update best
                self.bestScore = self.score
                self.brain.model.save()
                with open("bestScore.txt", "w") as f:
                    f.write(str(self.bestScore))
            print(f"Game: {self.round}, Score: {self.score}, Best Score: {self.bestScore}")
            return self.respawn()

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
        headCenter = Point(int((self.x + 0.5)*BLOCK_SIZE), 
                           int((self.y + 0.5)*BLOCK_SIZE))
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
        if (BOARD_ROWS * BOARD_COLS <= len(self.body) + 1): return DEAD_REWARD # Finished
        if self.x >= BOARD_COLS or self.x < 0: return DEAD_REWARD # Collide with wall
        if self.y >= BOARD_ROWS or self.y < 0: return DEAD_REWARD
        if self.pointInBody(Point(self.x, self.y)): return DEAD_REWARD # Collide with self
        if (self == self.apple):
            self.addCount += 1
            self.score += 1
            self.apple.randomize(self)
            return GROW_REWARD
        return NONE_REWARD # Do nothing

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
        snake.update() # To make sure draw the current version
        snake.draw()

        pygame.display.update()


if __name__ == "__main__":
    main()
