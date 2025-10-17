import argparse
import pygame
import os
import sys
import time

from src.solve import solve

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

# Global Variables
g_solution_dir = ".\solutions"
g_level = -1
g_walls = set()
g_boxes = set()
g_goals = set()
g_player = None
g_rows = 0
g_cols = 0

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
            elif cell == "$":
                boxes.add(pos)
            elif cell == "@":
                player = pos
            elif cell == ".":
                goals.add(pos)
            elif cell == "*":
                goals.add(pos)
                boxes.add(pos)
            elif cell == "+":
                goals.add(pos)
                player.add(pos)
    return walls, boxes, goals, player, len(lines), (max(len(line) for line in lines))

# --- SAVE SOLUTION ---
def save_solution(path):
    # Add solution to file
    os.makedirs(g_solution_dir, exist_ok=True)

    solution_file = os.path.join(g_solution_dir, f"level_{g_level}_solution.txt")
    with open(solution_file, "w") as file:
        num = 0
        file.write(f"Solution for level {g_level}, steps: {len(path)-1}\n")
        for s in path:
            file.write(f"Step {num}:{s.player}\n")
            num += 1
    print("Solution added to ", solution_file)

# --- GAME LOOP ---
def main():
    parser = argparse.ArgumentParser(description="Simple Sokoban Game")
    parser.add_argument("--level", type=int, default=1, help="Level number to load")
    parser.add_argument("--solve", type=int, default=0, help="Auto-solve the level (1 to enable)")
    args = parser.parse_args()
    g_level = args.level
    
    pygame.init()
    clock = pygame.time.Clock()

    # Load map
    walls, boxes, goals, player, rows, cols = load_level(g_level)

    # prepare animation variables
    anim_path = None
    anim_index = 0
    anim_last_time = 0
    ANIM_DELAY_MS = 200
    
    if args.solve:
        # compute solution path (list of State)
        path = solve(walls, player, boxes, goals)
        if path:
            print("Solved! Steps:", len(path)-1)
            save_solution(path)
            anim_path = path
            anim_index = 0
            anim_last_time = pygame.time.get_ticks()
        else:
            print("No solution found.")

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

                    # Di chuyển người chơi (only if not animating)
                    if anim_path is None:
                        player = new_pos
                        
        # --- Animation update (if we have a solution path) ---
        if anim_path is not None:
            now = pygame.time.get_ticks()
            if now - anim_last_time >= ANIM_DELAY_MS:
                anim_last_time = now
                anim_index += 1
                if anim_index < len(anim_path):
                    s = anim_path[anim_index]
                    player = s.player
                    boxes = set(s.boxes)
                else:
                    # finished animation
                    print("---Animation finished---")
                    anim_path = None


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