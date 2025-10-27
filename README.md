# SOKOBAN - Game & Solver

A Sokoban project with graphical interface and automatic solver using search algorithms.

## 📋 Description

Sokoban is a classic puzzle game where players move boxes to designated goal positions. This project includes:

- Sokoban game with graphical interface using Pygame
- Automatic solver with multiple search algorithms
- Support for 155+ levels

## ✨ Features

### Game Play

- Modern graphical interface with Pygame
- 155+ diverse levels
- Manual gameplay mode with arrow key controls
- Visual display of game states (player, boxes, goals, walls)

### AI Solver

- **DFS (Depth-First Search)**: Depth-first search algorithm
- **A\* Search**: Heuristic search algorithm with 3 heuristic functions:
  - **Manhattan Distance**: Manhattan distance from each box to nearest goal
  - **Bounded Relaxation (Static)**: Pre-computed shortest path from every cell to goal
  - **Bounded Relaxation (Dynamic)**: Dynamic heuristic with depth-based weight adjustment

### Additional Features

- Automatic solution animation display
- Save solutions to file
- Performance statistics (nodes explored/expanded, time, memory)
- Deadlock detection to avoid unsolvable states

## 🛠️ Installation

### Requirements

```bash
pip install pygame
pip install psutil
```

## 🚀 How to Run

```bash
python -m src.sokoban
```

## 📁 Project Structure

```
SOKOBAN/
├── src/
│   ├── sokoban.py      # Main game GUI and game loop
│   ├── solve.py        # Solver interface
│   ├── astar.py        # A* algorithm and heuristics implementation
│   ├── dfs.py          # DFS algorithm implementation
│   └── assets/         # Game assets
├── levels/             # 155+ levels (.txt files)
└── solutions/          # Auto-saved solutions (ignored in git)
```

## 🎮 Usage

### Playing the Game

1. Run the game: `python -m src.sokoban`
2. Click **"Play"** to start
3. Select a level and click **"PLAY"**
4. Use **arrow keys** to move the player and push boxes

### Using the Solver

1. Select the level you want to solve
2. Click **"SOLUTION"**
3. Choose an algorithm:
   - **DFS**: Depth-first search
   - **A\***: Heuristic search
4. If you choose A\*, select a heuristic:
   - Manhattan: Simple and fast
   - BoundRelaxation (Static): More accurate
   - BoundRelaxation (Dynamic): Adaptive weight
5. Watch the automatic solution animation
6. Solution is saved to `solutions/level_X_solution.txt`

## 📊 Level Format

Levels are saved as text files with the following characters:

- `#`: Wall
- `$`: Box
- `.`: Goal (target position)
- `@`: Player
- `*`: Box on goal
- `+`: Player on goal

Example:

```
#####
#.@.#
#$$$#
#####
```

## 🔍 Algorithms

### DFS (Depth-First Search)

- Depth-first search
- No heuristic required
- Suitable for small levels

### A\* Search

- Optimal heuristic search
- Uses `f(n) = g(n) + h(n)` where:
  - `g(n)`: Cost from start to current state
  - `h(n)`: Heuristic estimate from current state to goal
- Implemented heuristics:
  1. Manhattan Distance: `min(manhattan(box, goal))` for each box
  2. Bounded Relaxation: Sum of shortest paths from boxes to goals
  3. Dynamic: Adjust weight based on search depth

## 📝 Solution Format

Solutions are saved in `solutions/level_X_solution.txt`:

```
Solution for level 1
Algorithm: A*
Heuristic: Manhattan
Steps: 45
Nodes explored: 1234
Nodes expanded: 890
Nodes generated: 1500

Solution path:
Step 0: (2, 1)
Step 1: (3, 1)
...
```

## 🎯 Performance

Solver statistics:

- Nodes Explored**: Total nodes visited
- Nodes Expanded**: Nodes that have been expanded
- Nodes Generated**: Total nodes created
- Time: Solving time (seconds)
- Memory: Memory usage (KB)

## 📝 Notes

- The `solutions/` folder is automatically created when solving levels
- Solutions are not committed to git (ignored)
- Dynamic heuristic is suitable for complex levels
- Deadlock detection helps speed up the search

## 👥 Contributing

Welcome contributions! Please feel free to submit issues and pull requests.

## 📄 License

This project is open source.
