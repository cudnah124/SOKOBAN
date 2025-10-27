from typing import List, Set, Tuple, Optional

# Movement directions: up, down, left, right
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
class State:
    def __init__(self, player: Tuple[int, int], boxes: List[Tuple[int, int]]):
        self.player = player
        self.boxes = frozenset(boxes) 
    
    def __eq__(self, other) -> bool:
        """Check if two states are equal"""
        return self.player == other.player and self.boxes == other.boxes
    
    def __hash__(self) -> int:
        """Hash function for state comparison"""
        return hash((self.player, self.boxes))

def get_next_states(state: State, walls: Set[Tuple[int, int]], goals: Set[Tuple[int, int]]) -> List[State]:
    """Generate all possible next states from current state"""
    next_states = []
    px, py = state.player

    for dx, dy in DIRECTIONS:
        nx, ny = px + dx, py + dy

        # Check wall collision
        if (nx, ny) in walls:
            continue

        # Check box pushing
        if (nx, ny) in state.boxes:
            bx, by = nx + dx, ny + dy
            # Check if box can be pushed
            if (bx, by) in walls or (bx, by) in state.boxes:
                continue
            # Check for deadlock
            if is_deadlock((bx, by), walls, goals):
                continue
            # Create new state with pushed box
            new_boxes = set(state.boxes)
            new_boxes.remove((nx, ny))
            new_boxes.add((bx, by))
            next_states.append(State((nx, ny), new_boxes))
        else:
            # Simple move without pushing
            next_states.append(State((nx, ny), state.boxes))

    return next_states

def is_goal(state: State, goals: Set[Tuple[int, int]]) -> bool:
    """Check if all boxes are on goal positions"""
    return all(box in goals for box in state.boxes)

def is_deadlock(box_pos: Tuple[int, int], walls: Set[Tuple[int, int]], 
                goals: Set[Tuple[int, int]]) -> bool:
    """Check if box position is in a deadlock state"""
    bx, by = box_pos
    
    # Box on goal is never deadlock
    if box_pos in goals:
        return False
    
    # Check corner deadlocks
    corner_checks = [
        ((bx - 1, by), (bx, by - 1)),  # Top-left corner
        ((bx - 1, by), (bx, by + 1)),  # Top-right corner
        ((bx + 1, by), (bx, by - 1)),  # Bottom-left corner
        ((bx + 1, by), (bx, by + 1))   # Bottom-right corner
    ]
    
    for (pos1, pos2) in corner_checks:
        if pos1 in walls and pos2 in walls:
            return True
    
    return False
        
class DFS:
    """Depth-First Search algorithm with node tracking"""
    
    def __init__(self, start_state: State, walls: Set[Tuple[int, int]], 
                 goals: Set[Tuple[int, int]]):
        """Initialize DFS solver"""
        self.start_state = start_state
        self.walls = walls
        self.goals = goals
        self.nodes_explored = 0
        self.nodes_expanded = 0
        self.nodes_generated = 1  # Count initial state
    
    def solve(self) -> Optional[List[State]]:
        stack = [(self.start_state, [self.start_state])]
        visited = set([self.start_state])

        while stack:
            state, path = stack.pop()
            self.nodes_explored += 1
            
            if is_goal(state, self.goals):
                return path

            # Generate neighbors
            neighbors = get_next_states(state, self.walls, self.goals)
            self.nodes_expanded += 1  # Count as expanded
            
            for next_state in neighbors:
                if next_state not in visited:
                    visited.add(next_state)
                    self.nodes_generated += 1
                    stack.append((next_state, path + [next_state]))
        return None
    
    def get_statistics(self) -> dict:
        return {
            'nodes_explored': self.nodes_explored,
            'nodes_expanded': self.nodes_expanded,
            'nodes_generated': self.nodes_generated
        }

def dfs_solver(start_state: State, walls: Set[Tuple[int, int]], 
               goals: Set[Tuple[int, int]]) -> Tuple[Optional[List[State]], Optional[dict]]:
    dfs_algorithm = DFS(start_state, walls, goals)
    path = dfs_algorithm.solve()
    return path, dfs_algorithm.get_statistics()