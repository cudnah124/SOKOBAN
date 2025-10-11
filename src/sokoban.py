import argparse
import pygame
import os
import sys

# --- CONFIG ---
TILE_SIZE = 64
FPS = 60

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)

# --- LOAD LEVEL ---
def load_level(level):
    filename = os.path.join("levels", f"level{level}.txt")
    with open(filename, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    walls, boxes, goals = set(), set(), set()
    player = None

    for i, row in enumerate(lines):
        for j, cell in enumerate(row):
            pos = (j, i)
            if cell == "#":
                walls.add(pos)
            elif cell == "B":
                boxes.add(pos)
            elif cell == "P":
                player = pos
            elif cell == "G":
                goals.add(pos)
            elif cell == "X":
                goals.add(pos)
                boxes.add(pos)
    return walls, boxes, goals, player, len(lines), (max(len(line) for line in lines))

# --- GAME LOOP ---
def main():
    parser = argparse.ArgumentParser(description="Simple Sokoban Game")
    parser.add_argument("--level", type=int, default=1, help="Level number to load")
    args = parser.parse_args()
    
    pygame.init()
    clock = pygame.time.Clock()

    # Load map
    walls, boxes, goals, player, rows, cols = load_level(args.level)

    # Tạo cửa sổ
    screen = pygame.display.set_mode((cols*TILE_SIZE, rows*TILE_SIZE))
    pygame.display.set_caption("Sokoban - Pygame version")

    running = True
    while running:
        clock.tick(FPS)

        # --- Event ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dx, dy = 0, -1
                elif event.key == pygame.K_DOWN:
                    dx, dy = 0, 1
                elif event.key == pygame.K_LEFT:
                    dx, dy = -1, 0
                elif event.key == pygame.K_RIGHT:
                    dx, dy = 1, 0

                if dx != 0 or dy != 0:
                    new_pos = (player[0] + dx, player[1] + dy)

                    # Nếu đụng tường thì bỏ qua
                    if new_pos in walls:
                        continue

                    # Nếu gặp thùng
                    if new_pos in boxes:
                        box_new_pos = (new_pos[0] + dx, new_pos[1] + dy)
                        # Nếu sau thùng có tường hoặc thùng khác thì không đẩy được
                        if box_new_pos in walls or box_new_pos in boxes:
                            continue
                        # Đẩy thùng
                        boxes.remove(new_pos)
                        boxes.add(box_new_pos)

                    # Di chuyển người chơi
                    player = new_pos

        # --- Kiểm tra thắng ---
        if all(box in goals for box in boxes):
            print("---You Win!---")
            running = False

        # --- Render ---
        screen.fill(WHITE)

        # Tường
        for (x, y) in walls:
            pygame.draw.rect(screen, GRAY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Goals
        for (x, y) in goals:
            pygame.draw.circle(screen, YELLOW, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//6)

        # Boxes
        for (x, y) in boxes:
            pygame.draw.rect(screen, BLUE, (x*TILE_SIZE+8, y*TILE_SIZE+8, TILE_SIZE-16, TILE_SIZE-16))

        # Player
        pygame.draw.circle(screen, RED, (player[0]*TILE_SIZE+TILE_SIZE//2, player[1]*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//3)

        pygame.display.flip()

    # Thoát game
    pygame.quit()

if __name__ == "__main__":
    main()