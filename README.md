# Basic Sokoban Game
## How to run:
    python -m src.sokoban

## Test states:
    Modify `g_render_state` line 252 file sokoban.py to test playing and solving
`g_render_state = RENDER_PLAYING`: play a selected level (adjust g_current_level to an available level in `.\levels`, ex: `g_current_level = 1`)
`g_render_state = RENDER_SOLVING`: solve a selected level (adjust g_current_level to an available level in `.\levels`, ex: `g_current_level = 1`), the system will automatically solve that level, when it finishes, it will play a small animation to demonstrate it's solution.