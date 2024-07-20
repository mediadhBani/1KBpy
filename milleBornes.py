# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI
from milleBornes.rules import BadMove, BadParse


if __name__ == "__main__":
    game = Game(CLI())
    game.prepare()

    while True:
        game.start_turn()
        game.render_state()
        
        try:
            game.prompt_action()
            game.do_action()
        except (BadMove, BadParse) as exc:
            game.pass_error(exc)
        except EOFError:
            break
        
        if game.is_over():
            break

    game.conclude()

