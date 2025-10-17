from src.dfs import dfs
from src.dfs import State

import time
import os
import psutil

METHOD_DFS = 0
METHOD_ASTAR = 1

def solve(walls, player, boxes, goals, method=METHOD_DFS):

    proc = psutil.Process(os.getpid())
    before_mem = proc.memory_info().rss
    start_state = State(player, boxes)
    start_time = time.perf_counter()

    path = None
    if method == METHOD_DFS:
        path = dfs(start_state, walls, goals)
    elif method == METHOD_ASTAR:
        # CALL A* SOLVER HERE
        # Ex: path = astar(start_state, walls, goals)
        # start_state: initial state of the game
        # walls: set of wall positions
        # goals: set of goal positions
        pass

    end_time = time.perf_counter()
    after_mem = proc.memory_info().rss
    
    elapsed_time = end_time - start_time
    memory_used = after_mem - before_mem
    
    print(f"Time taken: {elapsed_time:.3f} seconds")
    print(f"RSS before: {before_mem} Bytes, after: {after_mem} Bytes, delta: {(memory_used)} Bytes")
    return path
