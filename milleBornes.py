# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI


if __name__ == "__main__":
    game = Game(CLI())
    game.run()

