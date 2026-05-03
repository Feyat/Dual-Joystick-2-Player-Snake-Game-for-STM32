import pygame
import serial
import random

ser = serial.Serial('/dev/tty.usbserial-0001', 115200, timeout=0.01)

pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Oyunculu Snake (Mac)")

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

def spawn_food(snake1, snake2):
    while True:
        x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        if (x, y) not in snake1 and (x, y) not in snake2:
            return (x, y)

def move_snake(snake, direction):
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    snake.insert(0, head)
    snake.pop()

def grow_snake(snake, direction):
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    snake.insert(0, head)

def normalize(value):
    if value < 7:
        return 0
    elif value > 300:
        return 1
    else:
        return 2

def update_direction(x, y, current_dir):
    if x == 0:
        return (-CELL_SIZE, 0)
    elif x == 1:
        return (CELL_SIZE, 0)
    elif y == 0:
        return (0, CELL_SIZE)
    elif y == 1:
        return (0, -CELL_SIZE)
    return current_dir

def check_collision(snake, other_snake):
    if snake[0] in snake[1:] or snake[0] in other_snake:
        return True
    x, y = snake[0]
    return x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT

def reset_game():
    global snake1, snake2, dir1, dir2, score1, score2, food
    snake1 = [(100, 100)]
    snake2 = [(300, 300)]
    dir1 = (CELL_SIZE, 0)
    dir2 = (-CELL_SIZE, 0)
    score1 = 0
    score2 = 0
    food = spawn_food(snake1, snake2)

FPS = 1
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
reset_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    last_line = None
    while ser.in_waiting:
        try:
            last_line = ser.readline().decode(errors='ignore').strip()
        except:
            pass

    if last_line:
        parts = last_line.split(',')
        if len(parts) == 4:
            try:
                p1_x, p1_y, p2_x, p2_y = [normalize(int(x)) for x in parts]
                dir1 = update_direction(p1_x, p1_y, dir1)
                dir2 = update_direction(p2_x, p2_y, dir2)
            except ValueError:
                pass

    move_snake(snake1, dir1)
    move_snake(snake2, dir2)

    for snake, direction, player in [(snake1, dir1, 1), (snake2, dir2, 2)]:
        if snake[0] == food:
            if player == 1:
                score1 += 1
            else:
                score2 += 1
            grow_snake(snake, direction)
            food = spawn_food(snake1, snake2)

    if check_collision(snake1, snake2):
        print("Oyuncu 1 kaybetti! Skor:", score1)
        reset_game()
    if check_collision(snake2, snake1):
        print("Oyuncu 2 kaybetti! Skor:", score2)
        reset_game()

    screen.fill(BLACK)
    pygame.draw.rect(screen, RED, (*food, CELL_SIZE, CELL_SIZE))
    for s in snake1:
        pygame.draw.rect(screen, GREEN, (*s, CELL_SIZE, CELL_SIZE))
    for s in snake2:
        pygame.draw.rect(screen, BLUE, (*s, CELL_SIZE, CELL_SIZE))
    score_text = font.render(f"P1: {score1}  P2: {score2}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
