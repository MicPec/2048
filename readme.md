Grid2048
--------

2048 game grid engine written for fun in Python. It can be used as a library or as a standalone game. It also has a Kivy GUI version.

![2048kivy.py](2048kivy.png)

No dependencies for the engine and CLI game (pure Python). For Kivy version, Kivy must be installed of course.

## Usage

```python
from grid2048 import DIRECTION, Grid2048, MoveFactory

grid = Grid2048(width, height)
move = MoveFactory.create(DIRECTION.UP)
moved = grid.move(move)
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

## Players

There is a possibility to add a custom player class. See `players/user_player.py` for example.
In `players.py` module are abstract classes for `Player` and `AIPlayer`. You can implement your own player class by inheriting from them and overriding `play` method.
Few example AI players are included: Monte Carlo Tree Search, Minimax and Expectimax: `mcts` ,`minimax`, `expectimax` respectively. 
Evaluation functions still need to be improved, but it's a good start.
Also, there is a random player: `random` and `cycle` player that cycle through directions.


## Play

There are two simple game examples:
- 2048.py - CLI version, use `u`, `d`, `l`, `r` keys.
- 2048kivy.py - GUI version using [Kivy](https://kivy.org), use the arrow keys.

The default player is `user`, but you can change it by passing `-p` argument. For example:

To run mcts player:
```bash
python ./2048.py -p mcts
```
or
```bash
python ./2048kivy.py -p mcts -i 10 
```
where `-i` is the interval between moves.
You can also pause the game by pressing `space` key, and move step by step by pressing `enter` key.

Also, you can set the width and height of the grid:
```bash
python ./2048.py --rows 3 --cols 6
```

## TODO
- Evaluation functions for AI players still need to be improved.
- Optimize the code.
- Write the Cython version.
  
Have fun ;)