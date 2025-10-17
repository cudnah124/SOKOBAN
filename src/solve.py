from src.dfs import dfs

from src.state import State
import time
import sys
import os
import psutil

def solve(walls, player, boxes, goals):

    proc = psutil.Process(os.getpid())
    before_mem = proc.memory_info().rss
    start_state = State(player, boxes)
    start_time = time.perf_counter()

    # dfs solution
    path = dfs(start_state, walls, goals)
    
    end_time = time.perf_counter()
    after_mem = proc.memory_info().rss
    
    elapsed_time = end_time - start_time
    memory_used = after_mem - before_mem
    
    print(f"Time taken: {elapsed_time:.3f} seconds")
    print(f"RSS before: {before_mem} Bytes, after: {after_mem} Bytes, delta: {(memory_used)} Bytes")
    return path
