from src.state import State
from src.state import DIRS

g_goals = set()

def get_next_states(state, walls):
    next_states = []
    px, py = state.player

    for dx, dy in DIRS:
        nx, ny = px + dx, py + dy

        if (nx, ny) in walls:
            continue

        if (nx, ny) in state.boxes:
            bx, by = nx + dx, ny + dy
            if (bx, by) in walls or (bx, by) in state.boxes:
                continue
            if is_deadlock((bx, by), walls):
                continue
            new_boxes = set(state.boxes)
            new_boxes.remove((nx, ny))
            new_boxes.add((bx, by))
            next_states.append(State((nx, ny), new_boxes))
        else:
            next_states.append(State((nx, ny), state.boxes))

    return next_states

def is_goal(state):
    return all(box in g_goals for box in state.boxes)

def is_deadlock(box_pos, walls):
    bx, by = box_pos
    if box_pos in g_goals:
        return False
    if (bx - 1, by) in walls and (bx, by - 1) in walls:
        return True
    if (bx - 1, by) in walls and (bx, by + 1) in walls:
        return True
    if (bx + 1, by) in walls and (bx, by - 1) in walls:
        return True
    if (bx + 1, by) in walls and (bx, by + 1) in walls:
        return True
        

def dfs(start_state, walls, goals):
    stack = [(start_state, [start_state])]
    visited = set([start_state])
    global g_goals
    g_goals = goals

    while stack:
        state, path = stack.pop()
        if is_goal(state):
            return path

        for next_state in get_next_states(state, walls):
            if next_state not in visited:
                visited.add(next_state)
                stack.append((next_state, path + [next_state]))
    return None