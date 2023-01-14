Grid2048
--------

2048 game grid engine written for fun in Python.

Also two simple game examples:
- 2048.py - CLI version, use `u`, `d`, `l`, `r` keys.
- 2048kivy.py - GUI version using [Kivy](https://kivy.org), use the arrow keys.

![2048kivy.py](2048kivy.png)

No dependencies for the engine and CLI game (pure Python). For Kivy version, Kivy must be installed of course.

## Usage

```python
from grid2048 import Grid2048

grid = Grid2048(width, height)

moved = grid.shift_down()
if moved:
    # do some staff, show score, etc. 
    print(grid)
    print(grid.score)   

if grid.no_moves():
    grid.reset()
```

## Customization

You can customize the grid size by specifying the `width` and `height` when initializing the `Grid2048` object. For example:
```python
grid = Grid2048(3, 6)  # Creates a 3x6 grid
```

## Update

Added posibility to add custom player class. See `2048.py` for example.
Example players are included in `players.py`.
Default player is `user`, but you can change it to one of few AI players including an option for Monte Carlo Tree Search, Minimax and Expectimax algorithm: `random`, `cycle`, `mcts` ,`minimax`, `expectimax`
Evaluation functions still needs to be improved, but it's a good start.

To run mcts player:
```bash
python ./2048.py -p mcts
```
or
```bash
python ./2048kivy.py -- -p mcts -i 10 
```
where `-i` is the interval between moves.

Also you can set the width and height of the grid:
```bash
python ./2048.py --rows 3 --cols 6
```

Have fun ;)