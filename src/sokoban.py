import pygame
import os

from src.solve import solve

# --- CONFIG ---
TILE_SIZE = 64
FPS = 60
ANIM_DELAY_MS = 200

# --- RENDER VARIABLES ---
RENDER_MAIN_MENU = 0
RENDER_LEVEL_SELECT = 1
RENDER_PLAYING = 2
RENDER_SOLVING = 3
RENDER_SOLVING_ANIM = 4
RENDER_HELP = 5
g_render_state = -1
g_screen = None
g_font = None

# --- SOLVING ANIMATION VARIABLES ---
anim_path = None
anim_index = 0
anim_last_time = 0

# --- COLORS ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)

# --- LEVELS DATA ---
LEVEL_FOLDER = "levels"
g_solution_dir = ".\solutions"
g_levels = None
g_current_level = 1
g_walls = set()
g_boxes = set()
g_goals = set()
g_player = None
g_rows = 0
g_cols = 0

# --- HANDLE KEY PRESS ---
g_key_pressed = None

# --- EVENT HANDLER ---
def event_handler():
    global g_key_pressed
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN and g_render_state == RENDER_PLAYING:
            g_key_pressed = event.key
            return True
    return True

# --- LOAD LEVEL ---
def load_level(level):
    filename = os.path.join(LEVEL_FOLDER, f"level{level}.txt")
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
                print("Found player at", pos)
                player = pos
            elif cell == ".":
                goals.add(pos)
            elif cell == "*":
                goals.add(pos)
                boxes.add(pos)
            elif cell == "+":
                goals.add(pos)
                player = pos
    return walls, boxes, goals, player, len(lines), (max(len(line) for line in lines))

# --- SAVE SOLUTION ---
def save_solution(path):
    # Add solution to file
    os.makedirs(g_solution_dir, exist_ok=True)

    solution_file = os.path.join(g_solution_dir, f"level_{g_current_level}_solution.txt")
    with open(solution_file, "w") as file:
        num = 0
        file.write(f"Solution for level {g_current_level}, steps: {len(path)-1}\n")
        for s in path:
            file.write(f"Step {num}:{s.player}\n")
            num += 1
    print("Solution added to ", solution_file)

# --- RENDER MOVE ---
def render_move():
    # --- Render ---
    g_screen.fill(WHITE)

    # Walls
    for (x, y) in g_walls:
        pygame.draw.rect(g_screen, GRAY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Goals
    for (x, y) in g_goals:
        pygame.draw.circle(g_screen, YELLOW, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//6)

    # Boxes
    for (x, y) in g_boxes:
        pygame.draw.rect(g_screen, BLUE, (x*TILE_SIZE+8, y*TILE_SIZE+8, TILE_SIZE-16, TILE_SIZE-16))

    # Player
    if g_player is None:
        print("render_move: player is None — check level file for player '@' or '+' marker")
        return
    pygame.draw.circle(g_screen, RED, (g_player[0]*TILE_SIZE+TILE_SIZE//2, g_player[1]*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//3)
    
# --- RENDER MAIN MENU ---
def render_main_menu():
    pass

# --- RENDER LEVEL SELECT ---
def render_level_select():
    pass

# --- RENDER PLAY ---
def render_playing():
    global g_player
    global g_boxes
    global g_key_pressed
    
    dx, dy = 0, 0
    if g_key_pressed == pygame.K_UP:
        dx, dy = 0, -1
    elif g_key_pressed == pygame.K_DOWN:
        dx, dy = 0, 1
    elif g_key_pressed == pygame.K_LEFT:
        dx, dy = -1, 0
    elif g_key_pressed == pygame.K_RIGHT:
        dx, dy = 1, 0
    g_key_pressed = None
    
    if dx != 0 or dy != 0:
        new_pos = (g_player[0] + dx, g_player[1] + dy)

        # If hit wall, ignore
        if new_pos in g_walls:
            return

        # Encounter a box
        if new_pos in g_boxes:
            box_new_pos = (new_pos[0] + dx, new_pos[1] + dy)
            # Check for valid pushes
            if box_new_pos in g_walls or box_new_pos in g_boxes:
                return
            # Push box
            g_boxes.remove(new_pos)
            g_boxes.add(box_new_pos)

        # Move player
        g_player = new_pos

    # --- Render moves ---
    render_move()

# --- RENDER SOLVING ---
def render_solving():
    global g_render_state
    global anim_path
    global anim_index
    global anim_last_time
    global g_screen
    
    # compute solution path (list of State)
    path = solve(g_walls, g_player, g_boxes, g_goals)
    if path:
        print("Solved! Steps:", len(path)-1)
        save_solution(path)
        anim_path = path
        anim_index = 0
        anim_last_time = pygame.time.get_ticks()
        g_render_state = RENDER_SOLVING_ANIM
        g_screen = pygame.display.set_mode((g_cols*TILE_SIZE, g_rows*TILE_SIZE))
    else:
        print("No solution found.")

# --- RENDER SOLVING ANIM ---
def render_solving_anim():
    global anim_index
    global anim_path
    global anim_last_time
    global g_player
    global g_boxes
                    
    # --- Animation update (if we have a solution path) ---
    if anim_path is not None:
        now = pygame.time.get_ticks()
        if now - anim_last_time >= ANIM_DELAY_MS:
            anim_last_time = now
            anim_index += 1
            if anim_index < len(anim_path):
                s = anim_path[anim_index]
                g_player = s.player
                g_boxes = set(s.boxes)
            else:
                # finished animation
                print("---Animation finished---")
                anim_path = None
    
    # --- Render moves ---
    render_move()

# --- RENDER HELP ---
def render_help():
    pass

# --- RENDER STATE MACHINE ---
def render_state_machine():
    if g_render_state == RENDER_MAIN_MENU:
        pass
    elif g_render_state == RENDER_LEVEL_SELECT:
        pass
    elif g_render_state == RENDER_PLAYING:
        render_playing()
    elif g_render_state == RENDER_SOLVING:
        render_solving()
    elif g_render_state == RENDER_SOLVING_ANIM:
        render_solving_anim()
    elif g_render_state == RENDER_HELP:
        pass

# --- INIT GAME ---
def init_game():
    global g_render_state
    global g_levels
    global g_screen
    global g_font
    
    pygame.init()
    
    g_render_state = RENDER_PLAYING
    g_screen = pygame.display.set_mode((800, 600))
    g_font = pygame.font.SysFont("arial", 24)
    pygame.display.set_caption("Sokoban - Pygame version")
    g_levels = sorted([f for f in os.listdir(LEVEL_FOLDER) if f.endswith(".txt")])
    
# --- GAME LOOP ---
def main():
    
    # Initialize game
    init_game()
    
    clock = pygame.time.Clock()

    global g_walls
    global g_boxes
    global g_goals
    global g_player
    global g_rows
    global g_cols

    # Mock level testing
    g_walls, g_boxes, g_goals, g_player, g_rows, g_cols = load_level(g_current_level)

    # Create window
    # screen = pygame.display.set_mode((cols*TILE_SIZE, rows*TILE_SIZE))

    running = True
    while running:
        clock.tick(FPS)
        running = event_handler()
        render_state_machine()

        # # --- Check winning ---
        if all(box in g_goals for box in g_boxes) and g_render_state == RENDER_PLAYING:
            print("---You Win!---")
            running = False
        pygame.display.flip()

    # Thoát game
    pygame.quit()

if __name__ == "__main__":
    main()