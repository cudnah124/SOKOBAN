import pygame
import os
import sys

from src.solve import solve

# --- CONFIG ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PREVIEW_TILE_SIZE = 32
TILE_SIZE = 64
FPS = 60
ANIM_DELAY_MS = 200

# --- RENDER VARIABLES ---
RENDER_MAIN_MENU = 0
RENDER_LEVEL_SELECT = 1
RENDER_PLAYING = 2
RENDER_ALGORITHM_SELECTION = 3
RENDER_HEURISTIC_SELECTION = 4
RENDER_SOLVING = 5
RENDER_SOLVING_ANIM = 6
RENDER_HELP = 7
g_render_state = -1
g_screen = None
g_font = None

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
map_width = 0
map_height = 0

# --- MAIN MENU BUTTONS ---
main_menu_buttons = {
    "Play": pygame.Rect(SCREEN_WIDTH/2 - 100, 150, 200, 60),
    "Help": pygame.Rect(SCREEN_WIDTH/2 - 100, 250, 200, 60),
    "Exit": pygame.Rect(SCREEN_WIDTH/2 - 100, 350, 200, 60),
}

# --- LEVEL SELECT BUTTONS ---
level_select_buttons = {
    "PLAY": pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 130, 170, 50),
    "SOLUTION": pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 70, 170, 50),
    "<": pygame.Rect(50, SCREEN_HEIGHT - 100, 100, 50),
    ">": pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 100, 50)
}

# --- LEVEL SELECT VARIABLES ---
g_current_level_index = 0

# --- SOLVING ALGORITHM SELECTION ---
DFS = 0
ASTAR = 1
g_selected_algorithm = None
solving_algorithm_buttons = {
    "DFS": pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 - 100, 170, 50),
    "A*": pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 - 40, 170, 50)
}

# --- HEURISTIC SELECTION ---
g_selected_heuristic = None
heuristic_buttons = {
    "Manhattan": pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 150, 300, 50),
    "BoundRelaxation (Static)": pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 80, 300, 50),
    "BoundRelaxation (Dynamic)": pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 10, 300, 50)
}

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
LIGHT_BLUE = (150, 150, 255)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# --- HANDLE EVENT ---
g_key_pressed = None
g_click = False

# --- EVENT HANDLER ---
def event_handler():
    global g_key_pressed
    global g_click
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and g_render_state == RENDER_PLAYING:
            g_key_pressed = event.key
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            g_click = True
    return True

# --- LOAD LEVEL ---
def load_level(level):
    global g_walls
    global g_boxes
    global g_goals
    global g_player
    global g_rows
    global g_cols
    
    g_walls.clear()
    g_boxes.clear()
    g_goals.clear()
    g_player = None
    g_rows = 0
    g_cols = 0

    filename = os.path.join(LEVEL_FOLDER, f"level{level}.txt")
    with open(filename, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    for i, row in enumerate(lines):
        for j, cell in enumerate(row):
            pos = (j, i)
            if cell == "#":
                g_walls.add(pos)
            elif cell == "$":
                g_boxes.add(pos)
            elif cell == "@":
                g_player = pos
            elif cell == ".":
                g_goals.add(pos)
            elif cell == "*":
                g_goals.add(pos)
                g_boxes.add(pos)
            elif cell == "+":
                g_goals.add(pos)
                g_player = pos
    g_rows, g_cols = len(lines), (max(len(line) for line in lines))

# --- SAVE SOLUTION ---
def save_solution(path, algorithm_name, heuristic_name=None, stats=None):
    # Add solution to file
    os.makedirs(g_solution_dir, exist_ok=True)

    solution_file = os.path.join(g_solution_dir, f"level_{g_current_level}_solution.txt")
    with open(solution_file, "w") as file:
        # Write header information
        file.write(f"Solution for level {g_current_level}\n")
        file.write(f"Algorithm: {algorithm_name}\n")
        if heuristic_name:
            file.write(f"Heuristic: {heuristic_name}\n")
        file.write(f"Steps: {len(path)-1}\n")
        
        # Write statistics if available
        if stats:
            file.write(f"Nodes explored: {stats['nodes_explored']}\n")
            file.write(f"Nodes expanded: {stats['nodes_expanded']}\n")
            file.write(f"Nodes generated: {stats['nodes_generated']}\n")
        
        file.write("\nSolution path:\n")
        
        # Write solution steps
        num = 0
        for s in path:
            file.write(f"Step {num}:{s.player}\n")
            num += 1
    print("Solution added to ", solution_file)

# --- RENDER MOVE ---
def render_move():
    global g_render_state
    global g_current_level_index
    global g_click
    global g_screen
    
    # --- Render ---
    g_screen.fill(WHITE)

    # Walls
    for (x, y) in g_walls:
        pygame.draw.rect(g_screen, GRAY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Goals
    for (x, y) in g_goals:
        pygame.draw.circle(g_screen, GOLD, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//6)

    # Boxes
    for (x, y) in g_boxes:
        if (x, y) in g_goals:
            pygame.draw.rect(g_screen, GREEN, (x*TILE_SIZE+8, y*TILE_SIZE+8, TILE_SIZE-16, TILE_SIZE-16))
            continue
        pygame.draw.rect(g_screen, BROWN, (x*TILE_SIZE+8, y*TILE_SIZE+8, TILE_SIZE-16, TILE_SIZE-16))

    # Player
    if g_player is None:
        print("render_move: player is None — check level file for player '@' or '+' marker")
        return
    pygame.draw.circle(g_screen, BLUE, (g_player[0]*TILE_SIZE+TILE_SIZE//2, g_player[1]*TILE_SIZE+TILE_SIZE//2), TILE_SIZE//3)

    back_button = { "BACK": pygame.Rect((g_cols*TILE_SIZE)//2 - 75, (g_rows*TILE_SIZE) + 10, 170, 50)}
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in back_button.items():
        color = LIGHT_BLUE if rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(g_screen, color, rect, border_radius=10)
        draw_text(text, g_font, WHITE, g_screen, rect.centerx, rect.centery)
        
        if g_click and rect.collidepoint(mouse_pos):
            g_click = False
            if text == "BACK":
                g_render_state = RENDER_LEVEL_SELECT
                g_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- TEXT DRAWING ---
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

# --- RENDER MAIN MENU ---
def render_main_menu():
    global g_render_state
    global g_click
    global g_current_level_index
    global g_screen
    
    g_screen.fill(WHITE)

    mouse_pos = pygame.mouse.get_pos()

    for text, rect in main_menu_buttons.items():
        color = LIGHT_BLUE if rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(g_screen, color, rect, border_radius=10)
        draw_text(text, g_font, WHITE, g_screen, rect.centerx, rect.centery)

        # Kiểm tra click
        if g_click and rect.collidepoint(mouse_pos):
            g_click = False
            if text == "Play":
                g_render_state = RENDER_LEVEL_SELECT
                g_current_level_index = 0
            elif text == "Help":
                g_render_state = RENDER_HELP
            elif text == "Exit":
                pygame.quit()
                sys.exit()

# --- LOAD LEVEL PREVIEW ---
def load_level_preview(filename):
    with open(os.path.join(LEVEL_FOLDER, filename), "r") as f:
        lines = [line.rstrip("\n") for line in f]
    return lines

# --- DRAW LEVEL PREVIEW ---
def draw_level_preview(level_data, x, y, tile_size=PREVIEW_TILE_SIZE):
    for row_idx, row in enumerate(level_data):
        for col_idx, ch in enumerate(row):
            rect = pygame.Rect(x + col_idx * tile_size, y + row_idx * tile_size, tile_size, tile_size)
            if ch == '#':
                pygame.draw.rect(g_screen, GRAY, rect) # Wall
            elif ch == '$':
                pygame.draw.rect(g_screen, BROWN, (2 + x + col_idx * tile_size, 2 + y + row_idx * tile_size, tile_size - 4, tile_size - 4))  # Brown box
            elif ch == '.':
                pygame.draw.circle(g_screen, GOLD, rect.center, tile_size // 2 - 8) # Goal
            elif ch == '@':
                pygame.draw.circle(g_screen, BLUE, rect.center, tile_size // 2 - 4) # Player
            elif ch == '*':
                pygame.draw.rect(g_screen, GREEN, (2 + x + col_idx * tile_size, 2 + y + row_idx * tile_size, tile_size - 4, tile_size - 4)) # Box on goal
            elif ch == '+':
                pygame.draw.circle(g_screen, BLUE, rect.center, tile_size // 2 - 4) # Player on goal

# --- RENDER LEVEL SELECT ---
def render_level_select():
    global g_current_level_index
    global g_render_state
    global g_click
    global g_screen
    global map_width
    global map_height

    g_screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    for text, rect in level_select_buttons.items():
        color = LIGHT_BLUE if rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(g_screen, color, rect, border_radius=10)
        draw_text(text, g_font, WHITE, g_screen, rect.centerx, rect.centery)

        # Kiểm tra click
        if g_click and rect.collidepoint(mouse_pos):
            g_click = False
            if text == "PLAY":
                # g_render_state = PLAY
                g_render_state = RENDER_PLAYING
                load_level(g_current_level_index + 1)
                g_screen = pygame.display.set_mode((g_cols*TILE_SIZE, g_rows*TILE_SIZE + 70))
                return
            if text == "SOLUTION":
                g_render_state = RENDER_ALGORITHM_SELECTION
                return
            elif text == "<":
                g_current_level_index = (g_current_level_index - 1) % len(g_levels)
            elif text == ">":
                g_current_level_index = (g_current_level_index + 1) % len(g_levels)

    # --- Display level ---
    if g_levels:
        level_data = load_level_preview(g_levels[g_current_level_index])
        level_name = g_levels[g_current_level_index].replace(".txt", "")
        txt = g_font.render(level_name, True, BLACK)
        g_screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 50))

        # Render map preview
        tile_size = 24
        rows = len(level_data)
        cols = max(len(line) for line in level_data)

        # Calculate render position
        map_width = cols * tile_size
        map_height = rows * tile_size
        start_x = (SCREEN_WIDTH - map_width) // 2
        start_y = (SCREEN_HEIGHT - map_height) // 2 - 50

        # Render map preview in center
        draw_level_preview(level_data, start_x, start_y, tile_size)

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
    global map_height
    global map_width
    global g_selected_heuristic
    
    # Map heuristic names to internal names
    heuristic_map = {
        "Manhattan": "Manhattan",
        "BoundRelaxation (Static)": "BoundRelaxation (Static)",
        "BoundRelaxation (Dynamic)": "BoundRelaxation (Dynamic)"
    }
    
    heuristic_name = heuristic_map.get(g_selected_heuristic, "BoundRelaxation (Static)")
    
    # Save algorithm
    if g_selected_algorithm == DFS:
        algorithm_name = "DFS"
    else:
        algorithm_name = "A*"
    
    # compute solution path (list of State)
    path, stats = solve(g_walls, g_player, g_boxes, g_goals, map_width, map_height, g_selected_algorithm, heuristic_name=heuristic_name)
    if path:
        print("Solved! Steps:", len(path)-1)
        
        # Save solution with algorithm and heuristic info
        if g_selected_algorithm == ASTAR:
            save_solution(path, algorithm_name, heuristic_name, stats)
        else:
            save_solution(path, algorithm_name, None, stats)
        
        anim_path = path
        anim_index = 0
        anim_last_time = pygame.time.get_ticks()
        g_render_state = RENDER_SOLVING_ANIM
        g_screen = pygame.display.set_mode((g_cols*TILE_SIZE, g_rows*TILE_SIZE + 70))
    else:
        print("No solution found.")

# --- RENDER SELECT SOLVING ALGORITHM ---
def render_select_solving_algorithm():
    global g_current_level_index
    global g_render_state
    global g_click
    global g_screen
    global g_selected_algorithm
    global g_current_level
    
    g_screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    
    for text, rect in solving_algorithm_buttons.items():
        color = LIGHT_BLUE if rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(g_screen, color, rect, border_radius=10)
        draw_text(text, g_font, WHITE, g_screen, rect.centerx, rect.centery)

        # Kiểm tra click
        if g_click and rect.collidepoint(mouse_pos):
            g_click = False
            if text == "DFS":
                g_render_state = RENDER_SOLVING
                g_selected_algorithm = DFS
                g_current_level = g_current_level_index + 1
                load_level(g_current_level_index + 1)
                return
            if text == "A*":
                g_render_state = RENDER_HEURISTIC_SELECTION
                return

# --- RENDER HEURISTIC SELECTION ---
def render_heuristic_selection():
    global g_current_level_index
    global g_render_state
    global g_click
    global g_screen
    global g_selected_algorithm
    global g_current_level
    global g_selected_heuristic
    
    g_screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    
    # Draw title
    draw_text("Select Heuristic", g_font, BLACK, g_screen, SCREEN_WIDTH//2, 100)
    
    for text, rect in heuristic_buttons.items():
        color = LIGHT_BLUE if rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(g_screen, color, rect, border_radius=10)
        draw_text(text, g_font, WHITE, g_screen, rect.centerx, rect.centery)

        # Kiểm tra click
        if g_click and rect.collidepoint(mouse_pos):
            g_click = False
            g_selected_heuristic = text
            g_render_state = RENDER_SOLVING
            g_selected_algorithm = ASTAR
            g_current_level = g_current_level_index + 1
            load_level(g_current_level_index + 1)
            return

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
    global g_render_state
    global g_screen
    global g_click
    
    g_screen.fill(WHITE)
    # Draw help text
    lines = [
        "Sokoban - Help",
        "",
        "Controls:",
        "  Arrow keys - move player",
        "  Click 'Play' to start a level",
        "  Click 'Help' to see this screen",
        "",
        "Solver:",
        "  Choose an algorithm from the SOLUTION menu to run the solver",
    ]
    start_y = 60
    for i, ln in enumerate(lines):
        draw_text(ln, g_font, BLACK, g_screen, SCREEN_WIDTH//2, start_y + i*30)

    # Place BACK button inside the visible window (below the help text)
    back_button = { "BACK": pygame.Rect((SCREEN_WIDTH)//2 - 75, SCREEN_HEIGHT - 80, 170, 50)}
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in back_button.items():
        color = LIGHT_BLUE if rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(g_screen, color, rect, border_radius=10)
        draw_text(text, g_font, WHITE, g_screen, rect.centerx, rect.centery)
        
        if g_click and rect.collidepoint(mouse_pos):
            g_click = False
            if text == "BACK":
                g_render_state = RENDER_MAIN_MENU

# --- RENDER STATE MACHINE ---
def render_state_machine():
    if g_render_state == RENDER_MAIN_MENU:
        render_main_menu()
    elif g_render_state == RENDER_LEVEL_SELECT:
        render_level_select()
    elif g_render_state == RENDER_PLAYING:
        render_playing()
    elif g_render_state == RENDER_ALGORITHM_SELECTION:
        render_select_solving_algorithm()
    elif g_render_state == RENDER_HEURISTIC_SELECTION:
        render_heuristic_selection()
    elif g_render_state == RENDER_SOLVING:
        render_solving()
    elif g_render_state == RENDER_SOLVING_ANIM:
        render_solving_anim()
    elif g_render_state == RENDER_HELP:
        render_help()

# --- TRACK LEVEL ---
def track_level():
    global g_levels
    
    files = [f for f in os.listdir(LEVEL_FOLDER) if f.endswith('.txt')]
    
    def _level_key(fname):
        name = fname
        if name.lower().startswith('level') and name.lower().endswith('.txt'):
            num_part = name[5:-4]  # strip 'level' and '.txt'
            try:
                return (0, int(num_part))
            except Exception:
                pass
        return (1, name)

    g_levels = sorted(files, key=_level_key)

# --- INIT GAME ---
def init_game():
    global g_render_state
    global g_levels
    global g_screen
    global g_font
    
    pygame.init()
    
    g_render_state = RENDER_MAIN_MENU
    g_screen = pygame.display.set_mode((800, 600))
    g_font = pygame.font.SysFont("arial", 24)
    pygame.display.set_caption("Sokoban - Pygame version")

    track_level()

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
    global g_render_state
    global g_screen

    # Mock level testing
    # g_walls, g_boxes, g_goals, g_player, g_rows, g_cols = load_level(g_current_level)

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
            g_render_state = RENDER_LEVEL_SELECT
            g_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.flip()

    # Thoát game
    pygame.quit()

if __name__ == "__main__":
    main()