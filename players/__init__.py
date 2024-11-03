from .player import PlayerFactory, AIPlayer
from .cycle_player import CyclePlayer
from .expectimax_player import ExpectimaxPlayer
from .mcs_player import MCSPlayer
from .mcts_player import MCTSPlayer
from .minimax_player import MinimaxPlayer
from .random_player import RandomPlayer
from .user_player import UserPlayer, KivyPlayer, PygamePlayer

player_factory = PlayerFactory()
player_factory.register("user", UserPlayer)
player_factory.register("random", RandomPlayer)
player_factory.register("cycle", CyclePlayer)
player_factory.register("mcts", MCTSPlayer)
player_factory.register("mcs", MCSPlayer)
player_factory.register("expectimax", ExpectimaxPlayer)
player_factory.register("minimax", MinimaxPlayer)
