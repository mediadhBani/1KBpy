# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI
from milleBornes.rules import BadMove


if __name__ == "__main__":
    game = Game(CLI)
    game.prepare()

    while not game.is_over():
        game.start_turn()
        game.render_state()
        
        try:
            game.prompt_action()
        except (EOFError, SystemExit):
            break

        try:
            game.do_action()
        except BadMove as exc:
            game.ui.errmsg = str(exc)

    game.conclude()

