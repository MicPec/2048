#!/usr/bin/env python
import argparse

import csv
import os
import time
from datetime import datetime
import multiprocessing

from grid2048 import Grid2048, helpers
from grid2048.hasher import Hasher
from players import player_factory

# disable user player for stats
del player_factory.container["user"]

WIDTH = 4
HEIGHT = 4


class Stats:
    """Play 2048 game and save stats to file.
    usage: 2048stats.py [-h] [-p PLAYER] [-i ITER] [-f FILE] [-o OPEN]
    options:
    -h, --help          show this help message and exit
    -p PLAYER, --player PLAYER
                        player type
    -i ITER, --iter ITER  number of iterations
    -f FILE, --file FILE  stats file
    -o OPEN, --open OPEN  open and show stats
    """

    stats_dir = "stats"
    fields = ["player", "score", "max_tile", "moves", "time", "grid"]

    def __init__(self, player: str | None = None, filename: str | None = None) -> None:
        self.player = player
        if not filename:
            self.filename = self._get_filename(player)
            return
        if filename and self.file_exists(filename):
            self.filename = filename
        else:
            f = f"{filename}.csv"
            self.filename = os.path.join(self.stats_dir, f)
        #     raise FileNotFoundError(f"File {filename!r} not found.")

    def file_exists(self, filename: str) -> bool:
        return os.path.exists(filename)

    def _get_filename(self, ai_player: str | None = None) -> str:
        """Generate filename for stats"""
        dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        f = f"{dt}_{ai_player}.csv"
        return os.path.join(self.stats_dir, f)

    def save_stats(self, stats: dict) -> None:
        """Save stats to file"""
        if not os.path.exists(self.stats_dir):
            os.mkdir(self.stats_dir)
        with open(self.filename, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            if os.path.getsize(self.filename) == 0:
                writer.writerow({fn: fn for fn in self.fields})
            writer.writerow(stats)

    def load_stats(self, filenme: str) -> list:
        """Load stats from file"""
        with open(filenme, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            return [dict(r) for r in reader]

    def print_stats(self, stats: list) -> None:
        """Print stats to console"""
        print(f"Total games: {len(stats):>9}")
        print(f"Total time: {sum(float(s['time']) for s in stats) / 60:>14.2f} min.")
        print(
            f"Mean time: {sum(float(s['time']) for s in stats) / len(stats) / 60:>13.2f} min."
        )
        print(
            f"Mean move time: {sum(float(s['time']) for s in stats) / sum(int(s['moves']) for s in stats):>8.2f} sec."
        )

        print("-" * 30)
        print(f"Max score: {max(int(s['score']) for s in stats):>14}")
        print(f"Min score: {min(int(s['score']) for s in stats):>13}")
        print(
            f"Average score: {sum(int(s['score']) for s in stats) / len(stats):>10.0f}"
        )
        print("-" * 30)
        print(f"Max moves: {max(int(s['moves']) for s in stats):>13}")
        print(f"Min moves: {min(int(s['moves']) for s in stats):>12}")
        print(
            f"Average moves: {sum(int(s['moves']) for s in stats) / len(stats):>9.0f}"
        )
        print("-" * 30)
        print(
            f"Wins count: {len([s for s in stats if int(s['max_tile']) >= 2048]):>10}"
        )
        print(
            f"Percentage of wins: {len([s for s in stats if int(s['max_tile']) >= 2048]) / len(stats) * 100:>3.2f}%"
        )
        # print(f"Max tile: {max(int(s['max_tile']) for s in stats):>14}")
        print("-" * 30)
        print(f"{'Max tile:':>6} {'count':>8} (percentage):")
        max_tile_count = {2**i: 0 for i in range(1, 16)}
        for s in stats:
            max_tile_count[int(s["max_tile"])] += 1
        for tile, count in max_tile_count.items():
            if count:
                print(f"{tile:>8}: {count:>8} ({count / len(stats) * 100:.2f}%)")

    def run(self, iteration: int) -> None:
        """Run the simulation certain number of iterations"""
        if not self.player:
            raise ValueError("Player type not specified.")
        stime = time.time()
        grid = Grid2048(WIDTH, HEIGHT)
        player = player_factory.create(self.player, grid)
        while not grid.no_moves:
            print("\t" * (iteration), f"{iteration+1}:{grid.score}", end="\r")
            player.play()
            # print(grid)
        etime = time.time() - stime
        self.process_stats(iteration, grid, etime)
        return

    def process_stats(self, iteration: int, grid: Grid2048, etime: float) -> None:
        h = Hasher(grid)
        stat = {
            "player": self.player,
            "score": grid.score,
            "max_tile": helpers.max_tile(grid),
            "moves": grid.moves,
            "time": etime,
            "grid": h.hash(),
        }
        self.save_stats(stat)
        print(grid)
        print(
            f"Game: {iteration} | score: {grid.score} | max tile: {helpers.max_tile(grid)} | moves: {grid.moves}",
            end="\n\n",
        )


def parse_cmd_args() -> tuple[str, int, int, str | None, str | None]:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--player", type=str, help="player type")
    parser.add_argument("-i", "--iter", type=str, help="number of iterations")
    parser.add_argument("-f", "--file", type=str, help="stats file")
    parser.add_argument("-o", "--open", type=str, help="open and show stats")
    parser.add_argument("-c", "--cores", type=str, help="how many cores to use")
    args = parser.parse_args()
    player = args.player or "random"
    if player not in player_factory.container:
        raise ValueError(f"Invalid player type: {player!r}")
    ffile = args.file
    fopen = args.open
    iterations = int(args.iter or 10)
    cores = int(args.cores) if args.cores else multiprocessing.cpu_count() // 2
    return (player, iterations, cores, ffile, fopen)


def main() -> None:
    player, iterations, cores, ffile, fopen = parse_cmd_args()

    if fopen:  # Show stats from file
        stats = Stats(filename=fopen)
        stats.print_stats(stats.load_stats(fopen))
        return
    # Start the game
    print(
        f"Starting {iterations} games with {WIDTH}x{HEIGHT} grid and {player!r} player"
    )
    stats = Stats(player, ffile)
    # TODO: refactor this
    with multiprocessing.Pool(cores) as pool:
        pool.map(stats.run, range(iterations))

    print("*" * 80)
    print(f"Stats saved to {stats.filename!r}")
    print("-" * 30)
    stats.print_stats(stats.load_stats(stats.filename))


if __name__ == "__main__":
    main()
