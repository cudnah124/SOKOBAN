from src.dfs import State, dfs
from src.astar import astar_solve

import time
import os
import psutil

METHOD_DFS = 0
METHOD_ASTAR = 1

def solve(walls, player, boxes, goals, map_width, map_height, method=METHOD_DFS):

    proc = psutil.Process(os.getpid())
    before_mem = proc.memory_info().rss
    start_state = State(player, boxes)
    start_time = time.perf_counter()

    path = None
    if method == METHOD_DFS:
        path = dfs(start_state, walls, goals)
    elif method == METHOD_ASTAR:
        # CALL A* SOLVER HERE
        path = astar_solve(start_state, walls, goals, map_width, map_height, heuristic_name="relaxation")
    end_time = time.perf_counter()
    after_mem = proc.memory_info().rss
    
    elapsed_time = end_time - start_time
    memory_used = after_mem - before_mem
    
    print(f"Time taken: {elapsed_time:.3f} seconds")
    print(f"RSS before: {before_mem} Bytes, after: {after_mem} Bytes, delta: {(memory_used)} Bytes")
    return path
