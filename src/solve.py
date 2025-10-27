from src.dfs import State, dfs_solver
from src.astar import astar_solve

import time
import os
import psutil

METHOD_DFS = 0
METHOD_ASTAR = 1

def solve(walls, player, boxes, goals, map_width, map_height, method=METHOD_DFS, heuristic_name="relaxation"):

    proc = psutil.Process(os.getpid())
    before_mem = proc.memory_info().rss
    start_state = State(player, boxes)
    start_time = time.perf_counter()

    path = None
    stats = None
    if method == METHOD_DFS:
        path, stats = dfs_solver(start_state, walls, goals)
    elif method == METHOD_ASTAR:
        path, stats = astar_solve(start_state, walls, goals, map_width, map_height, heuristic_name=heuristic_name)
        
    end_time = time.perf_counter()
    after_mem = proc.memory_info().rss
    
    elapsed_time = end_time - start_time
    memory_used = after_mem - before_mem
    if stats:
        print(f"Nodes explored: {stats['nodes_explored']}")
        print(f"Nodes expanded: {stats['nodes_expanded']}")
        print(f"Nodes generated: {stats['nodes_generated']}")
    print(f"Time taken: {elapsed_time:.3f} seconds")
    print(f"Memory used: {memory_used / 1024:.2f} KB")
    return path, stats
