DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

class State:
    def __init__(self, player, boxes):
        self.player = player
        self.boxes = frozenset(boxes) 
    
    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes
    
    def __hash__(self):
        return hash((self.player, self.boxes))
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
        
class DFS:
    """DFS algorithm with node tracking"""
    
    def __init__(self, start_state, walls, goals):
        self.start_state = start_state
        self.walls = walls
        self.goals = goals
        self.nodes_explored = 0
        self.nodes_expanded = 0
        self.nodes_generated = 1  # Initial state
    
    def solve(self):
        """Solve using DFS algorithm with tracking"""
        stack = [(self.start_state, [self.start_state])]
        visited = set([self.start_state])
        global g_goals
        g_goals = self.goals

        while stack:
            state, path = stack.pop()
            self.nodes_explored += 1
            
            if is_goal(state):
                return path

            # Generate neighbors
            neighbors = get_next_states(state, self.walls)
            self.nodes_expanded += 1  # Count as expanded
            
            for next_state in neighbors:
                if next_state not in visited:
                    visited.add(next_state)
                    self.nodes_generated += 1
                    stack.append((next_state, path + [next_state]))
        return None
    
    def get_statistics(self):
        """Return search statistics"""
        return {
            'nodes_explored': self.nodes_explored,
            'nodes_expanded': self.nodes_expanded,
            'nodes_generated': self.nodes_generated
        }

def dfs(start_state, walls, goals):
    """Original DFS function for backward compatibility"""
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