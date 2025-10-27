import heapq
from typing import List, Tuple, TypeVar, Generic, Callable, Optional, Set
from src.dfs import State
from collections import deque


#ASTAR NODE IMPLEMENT
T = TypeVar('T')

class Node(Generic[T]):
    """Represents a node in the search tree"""
    def __init__(self, state: T, g_score: int, h_score: int, parent: Optional['Node[T]'] = None, action: Optional[str] = None):
        self.state = state
        self.g_score = g_score  # Cost from start
        self.h_score = h_score  # Heuristic estimate to goal
        self.f_score = g_score + h_score  # Total estimated cost
        self.parent = parent
        self.action = action
    
    def __lt__(self, other: 'Node[T]') -> bool:
        """For heap comparison"""
        return self.f_score < other.f_score

class AStar(Generic[T]):
    """Generic A* algorithm implementation"""
    
    def __init__(self,
                 initial_state: T,
                 is_goal: Callable[[T], bool],
                 get_neighbors: Callable[[T], List[Tuple[T, str]]],
                 heuristic: Callable[[T], int],
                 state_key: Callable[[T], tuple] = None,
                 max_depth: int = 1000, epsilon: float = 1.0):
        """
        Initialize A* solver
        
        Args:
            initial_state: Starting state
            is_goal: Function to check if state is goal
            get_neighbors: Function to get (next_state, action) pairs
            heuristic: Function to estimate distance to goal
            state_key: Function to create hashable state identifier (for cycle detection)
            max_depth: Maximum search depth to prevent infinite loops
        """
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.get_neighbors = get_neighbors
        self.heuristic = heuristic
        self.state_key = state_key if state_key else lambda s: s
        self.max_depth = max_depth
        self.nodes_explored = 0
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.epsilon = epsilon
    
    def solve(self) -> Optional[List[str]]:
        """
        Solve using A* algorithm
        
        Returns:
            List of actions to reach goal, or None if no solution found
        """
        counter = 0
        initial_h = self.heuristic(self.initial_state, 0)
        start_node = Node(self.initial_state, 0, initial_h)
        self.nodes_generated = 1  # Count initial node
        
        heap = [(start_node.f_score, counter, start_node)]
        visited: Set[tuple] = set()
        
        while heap:
            _, _, current_node = heapq.heappop(heap)
            self.nodes_explored += 1
            
            # Check if goal
            if self.is_goal(current_node.state):
                return self._reconstruct_path(current_node)
            
            # Cycle detection
            state_key = self.state_key(current_node.state)
            if state_key in visited:
                continue
            visited.add(state_key)
            self.nodes_expanded += 1
            
            # Depth limit check
            if current_node.g_score >= self.max_depth:
                continue
            
            # Explore neighbors
            for next_state, action in self.get_neighbors(current_node.state):
                next_state_key = self.state_key(next_state)
                
                if next_state_key not in visited:
                    g_score = current_node.g_score + 1
                    h_score = self.epsilon * self.heuristic(next_state, g_score)
                    next_node = Node(next_state, g_score, h_score, current_node, action)
                    
                    counter += 1
                    self.nodes_generated += 1  # Count each generated node
                    heapq.heappush(heap, (next_node.f_score, counter, next_node))
        
        return None  # No solution found
    
    def _reconstruct_path(self, node: Node[T]) -> List[str]:
        """Reconstruct path from start to goal"""
        path = []
        current = node
        
        while current.parent is not None:
            if current.action:
                path.append(current.action)
            current = current.parent
        
        path.reverse()
        return path
    
    def get_statistics(self) -> dict:
        """Return search statistics"""
        return {
            'nodes_explored': self.nodes_explored,
            'nodes_expanded': self.nodes_expanded,
            'nodes_generated': self.nodes_generated
        }



#ASTAR SOLVE IMPLEMENT

# Global goals for heuristic calculation
g_goals = set()

def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two positions"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def precompute_goal_distances(walls: Set[Tuple[int, int]], goals: Set[Tuple[int, int]], width: int, height: int) -> dict:
    """
    Pre-computes the shortest distance from every non-wall tile to the nearest goal.
    Uses a multi-source Breadth-First Search (BFS) starting from all goals.
    """
    goal_distance_map = {}
    queue = deque()
    visited = set()

    # Initialize queue with all goal positions
    for goal in goals:
        queue.append((goal, 0))
        visited.add(goal)
        goal_distance_map[goal] = 0

    while queue:
        (x, y), dist = queue.popleft()

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            
            # Check boundaries and if the position is valid
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls and (nx, ny) not in visited:
                visited.add((nx, ny))
                goal_distance_map[(nx, ny)] = dist + 1
                queue.append(((nx, ny), dist + 1))
                
    return goal_distance_map

def heuristic_bounded_relaxation(state: State, goal_distance_map: dict, current_depth: int = 0) -> int:
    """
    Bounded Relaxation Heuristic.
    Sums the pre-computed shortest path cost for each box to its nearest goal.
    This relaxation assumes each box can be moved freely without other boxes blocking.
    """
    total_cost = 0
    for box in state.boxes:
        # If a box is in a position from which no goal is reachable, this path is a dead end.
        cost = goal_distance_map.get(box)
        if cost is None:
            return float('inf') # Dead end state
        total_cost += cost
    return total_cost

def heuristic_manhattan(state: State, current_depth: int = 0) -> int:
    """
    Heuristic function for A*
    Sum of minimum distances from each box to any target
    """
    global g_goals
    if not state.boxes or not g_goals:
        return 0
    
    total_distance = 0
    boxes_list = list(state.boxes)
    goals_list = list(g_goals)
    
    for box in boxes_list:
        min_dist = min(manhattan_distance(box, goal) for goal in goals_list)
        total_distance += min_dist
    
    return total_distance

def dynamic_heuristic(state: State, goal_distance_map: dict, current_depth: int = 0, max_depth: int = 500) -> int:
    """
    Dynamic heuristic that adjusts weight based on depth
    weight = (1 - d(n))/N if d(n) < N, else 0
    hd = hn * (1 + epsilon * weight )
    """
    base_heuristic = heuristic_bounded_relaxation(state, goal_distance_map, current_depth)
    if current_depth < max_depth:
        weight = (1 - current_depth / max_depth)
        return (1 + weight) * base_heuristic
    else:
        return 0

def get_neighbors_with_actions(state: State, walls, goals) -> List[Tuple[State, str]]:
    """Get all possible next states and the actions that produce them"""
    neighbors = []
    directions = [
        (-1, 0, 'UP'),
        (1, 0, 'DOWN'),
        (0, -1, 'LEFT'),
        (0, 1, 'RIGHT')
    ]
    
    px, py = state.player
    
    for dx, dy, direction in directions:
        nx, ny = px + dx, py + dy
        
        if (nx, ny) in walls:
            continue
        
        if (nx, ny) in state.boxes:
            bx, by = nx + dx, ny + dy
            if (bx, by) in walls or (bx, by) in state.boxes:
                continue
            # Simple deadlock check
            if is_simple_deadlock((bx, by), walls, goals):
                continue
            new_boxes = set(state.boxes)
            new_boxes.remove((nx, ny))
            new_boxes.add((bx, by))
            neighbors.append((State((nx, ny), new_boxes), direction))
        else:
            neighbors.append((State((nx, ny), state.boxes), direction))
    
    return neighbors

def is_simple_deadlock(box_pos, walls, goals):
    """Simple deadlock check without global dependency"""
    bx, by = box_pos
    if box_pos in goals:
        return False
    if (bx - 1, by) in walls and (bx, by - 1) in walls:
        return True
    if (bx - 1, by) in walls and (bx, by + 1) in walls:
        return True
    if (bx + 1, by) in walls and (bx, by - 1) in walls:
        return True
    if (bx + 1, by) in walls and (bx, by + 1) in walls:
        return True
    return False

def astar_solve(start_state: State, walls, goals, map_width, map_height, heuristic_name = "manhattan") -> Optional[List[State]]:
    """
    Solve Sokoban using A* algorithm
    
    Args:
        start_state: Initial game state
        walls: Set of wall positions
        goals: Set of goal positions
        
    Returns:
        List of states from start to goal, or None if no solution found
    """
    global g_goals
    # Ensure goals is a set
    if not isinstance(goals, set):
        goals = set(goals)
    g_goals = goals
    
    if heuristic_name == 'BoundRelaxation (Static)':
        goal_distance_map = precompute_goal_distances(walls, goals, map_width, map_height)
        heuristic_func = lambda state, depth: heuristic_bounded_relaxation(state, goal_distance_map, depth)
        epsilon = 1.0  # Weight for bounded relaxation
    elif heuristic_name == 'Manhattan':
        heuristic_func = lambda state, depth: heuristic_manhattan(state, depth)
        epsilon = 1.0  # Standard A*
    elif heuristic_name == 'BoundRelaxation (Dynamic)':
        goal_distance_map = precompute_goal_distances(walls, goals, map_width, map_height)
        heuristic_func = lambda state, depth: dynamic_heuristic(state, goal_distance_map, depth)
        epsilon = 1.0  # Dynamic weight

    def is_goal_state(state: State) -> bool:
        return all(box in g_goals for box in state.boxes)
    
    def get_neighbors(state: State) -> List[Tuple[State, str]]:
        return get_neighbors_with_actions(state, walls, goals)
    
    def state_key(state: State) -> tuple:
        return (state.player, tuple(sorted(state.boxes)))
    
    # Create A* solver
    solver = AStar(
        initial_state=start_state,
        is_goal=is_goal_state,
        get_neighbors=get_neighbors,
        heuristic=heuristic_func,
        state_key=state_key,
        max_depth=500,
        epsilon=epsilon
    )
    
    # Get solution as list of actions
    actions = solver.solve()
    
    if not actions:
        return None, solver.get_statistics()
    
    # Convert actions back to states
    current_state = start_state
    path = [current_state]
    
    for action in actions:
        # Find the next state by applying the action
        for next_state, next_action in get_neighbors_with_actions(current_state, walls, goals):
            if next_action == action:
                current_state = next_state
                path.append(current_state)
                break
    
    return path, solver.get_statistics()

