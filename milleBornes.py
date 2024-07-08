# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI
from milleBornes.rules import BadMove


if __name__ == "__main__":
    ui = CLI()
    game = Game(ui.prompt_number_players())

    while not game.is_over():
        game.pick_player()
        game.render_state()
        
        try:
            game.prompt_action()
        except (EOFError, SystemExit):
            break

        try:
            game.do_action()
        except BadMove as exc:
            game.ui.errmsg = str(exc)

    ui.display_game_end(game.players)

