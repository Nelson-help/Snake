import random
import pygame

pygame.init()

FPS = 10

WIDTH, HEIGHT = 1000, 750

BOARD_COLS = 20
BOARD_ROWS = 10

BLOCK_SIZE = min(WIDTH/BOARD_COLS, HEIGHT/BOARD_ROWS)

BORDER_WIDTH = int(BLOCK_SIZE/15)

SNAKE_INITIAL_LENGTH = 4

SNAKE_COLOR = (255, 171, 94)
APPLE_COLOR = (255, 100, 100)
BG_COLOR = (192, 255, 192)

LANDING_BG = pygame.image.load("Landing.png")
LANDING_BG = pygame.transform.scale(LANDING_BG, (WIDTH, HEIGHT))

END_BG = pygame.image.load("End.png")
END_BG = pygame.transform.scale(END_BG, (WIDTH, HEIGHT))

WIN_BG = pygame.image.load("Win.png")
WIN_BG = pygame.transform.scale(WIN_BG, (WIDTH, HEIGHT))

GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_WIN = 3

GAME_STATE = GAME_STATE_START

FONT = pygame.font.SysFont("georgia", 200)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()


class Point:
    x: int = 0
    y: int = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Snake(Point):
    def __init__(self):
        self.respawn()

    def respawn(self):
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
        if (self.x == p.x and self.y == p.y):
            return True

        return self.pointInBody(p)

    def pointInBody(self, p: Point):
        for block in self.body:
            if (block.x == p.x and block.y == p.y):
                return True
        return False

    def update(self):
        global GAME_STATE

        self.body.append(Point(self.x, self.y))
        self.x += self.vel.x
        self.y += self.vel.y

        if (self.addCount > 0):
            self.addCount -= 1
        else:
            self.body.pop(0)

        if (self.x >= BOARD_COLS or self.x < 0):
            GAME_STATE = GAME_STATE_GAME_OVER
            return
        if (self.y >= BOARD_ROWS or self.y < 0):
            GAME_STATE = GAME_STATE_GAME_OVER
            return

        if (self.pointInBody(Point(self.x, self.y))):
            GAME_STATE = GAME_STATE_GAME_OVER
            return

        if (len(self.body) + 1 == BOARD_COLS * BOARD_ROWS):
            GAME_STATE = GAME_STATE_WIN
            return

        if (self.x == self.apple.x and self.y == self.apple.y):
            self.addCount += 1
            self.score += 1
            self.apple.randomize(self)

        if (self.score >= BOARD_COLS * BOARD_ROWS):
            GAME_STATE = GAME_STATE_WIN
            return

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
        headCenter = Point((self.x + 0.5)*BLOCK_SIZE, (
            self.y + 0.5)*BLOCK_SIZE)
        delta = Point(self.vel.x * BLOCK_SIZE/4, self.vel.y * BLOCK_SIZE/4)
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


class Apple(Point):
    def __init__(self, snake: Snake):
        self.randomize(snake)

    def randomize(self, snake: Snake):
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


snake = Snake()


def main():
    global GAME_STATE, snake
    while (True):
        new_dir = Point(snake.vel.x, snake.vel.y)

        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return pygame.quit()

            if event.type == pygame.KEYDOWN:
                if GAME_STATE == GAME_STATE_START:
                    snake = Snake()
                    GAME_STATE = GAME_STATE_PLAYING

                if GAME_STATE == GAME_STATE_GAME_OVER:
                    GAME_STATE = GAME_STATE_START

                if GAME_STATE == GAME_STATE_PLAYING:
                    if event.key == pygame.K_UP and snake.vel.y != 1:
                        new_dir.x = 0
                        new_dir.y = -1
                    elif event.key == pygame.K_DOWN and snake.vel.y != -1:
                        new_dir.x = 0
                        new_dir.y = 1
                    elif event.key == pygame.K_LEFT and snake.vel.x != 1:
                        new_dir.x = -1
                        new_dir.y = 0
                    elif event.key == pygame.K_RIGHT and snake.vel.x != -1:
                        new_dir.x = 1
                        new_dir.y = 0

                if GAME_STATE == GAME_STATE_WIN:
                    GAME_STATE = GAME_STATE_START

        WINDOW.fill(BG_COLOR)
        if (GAME_STATE == GAME_STATE_START):
            WINDOW.blit(LANDING_BG, (0, 0))

        elif (GAME_STATE == GAME_STATE_PLAYING):
            label = FONT.render(f"{snake.score}", False, (255, 255, 255))
            w, h = label.get_size()
            WINDOW.blit(label, (int(WIDTH - w) / 2, int(HEIGHT - h) / 2))
            snake.draw()
            snake.vel = new_dir
            snake.update()

        elif (GAME_STATE == GAME_STATE_GAME_OVER):
            WINDOW.blit(END_BG, (0, 0))

        elif (GAME_STATE == GAME_STATE_WIN):
            WINDOW.blit(WIN_BG, (0, 0))

        pygame.display.update()


if __name__ == "__main__":
    main()
