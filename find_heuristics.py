import cma
import numpy as np
from grid2048.grid2048 import Grid2048
from players.expectimax_player import ExpectimaxPlayer
from players.mcts_player import MCTSPlayer
from players.minimax_player import MinimaxPlayer
from players.player import PlayerFactory

WIDTH = 4
HEIGHT = 4

player_factory = PlayerFactory()
player_factory.register("mcts", MCTSPlayer)
player_factory.register("expectimax", ExpectimaxPlayer)
player_factory.register("minimax", MinimaxPlayer)


class Game:
    def __init__(self, width: int, height: int, player_type: str) -> None:
        self.grid = Grid2048(width, height)
        self.player = player_factory.create(player_type, self.grid)

    def game_over(self) -> bool:
        return self.grid.no_moves


def heuristic(weights: list, game):
    game.player.evaluator.set_weight("pairs", weights[0])
    game.player.evaluator.set_weight("pairs", weights[1])
    game.player.evaluator.set_weight("pairs2", weights[2])
    game.player.evaluator.set_weight("pairs3", weights[3])
    game.player.evaluator.set_weight("smoothness", weights[4])
    game.player.evaluator.set_weight("monotonicity", weights[5])
    game.player.evaluator.set_weight("high_vals_on_edge", weights[6])
    game.player.evaluator.set_weight("high_vals_in_corner", weights[7])
    game.player.evaluator.set_weight("higher_on_edge", weights[8])
    game.player.evaluator.set_weight("score", weights[9])
    game.player.play()
    return game.grid.score


def objective_function(weights):
    scores = []
    game = Game(4, 4, "expectimax")
    for i in range(1000):
        # game.player.play()
        scores.append(heuristic(weights, game))
        print(i, weights, game.player.evaluator, game.grid)
        if game.game_over():
            break
    return -np.mean(scores)


def main() -> None:
    num_games = 10
    initial_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    sigma0 = 0.25

    res = cma.fmin(
        objective_function,
        initial_weights,
        sigma0,
        options={"verbose": -9, "maxfevals": num_games},
    )

    print(res[0])


if __name__ == "__main__":
    main()
