from src.dfs import dfs

from src.state import State
import time

def solve(walls, player, boxes, goals):

    start_state = State(player, boxes)
    start_time = time.perf_counter()

    # dfs solution
    path = dfs(start_state, walls, goals)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.3f} seconds")
    return path
