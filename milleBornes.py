# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI
from milleBornes.rules import BadMove


if __name__ == "__main__":
    ui = CLI()
    game = Game(ui.prompt_number_players())

    while not game.is_over():
        player = game.pick_player()
        game.render_state()
        
        try:
            card_idx = game.prompt_action()
        except (EOFError, SystemExit):
            break

        try:
            game.do_action()
        except BadMove as exc:
            game.ui.errmsg = str(exc)
            continue

        # la carte jouée est défaussée
        player.hand.pop(card_idx)
        game.turn_end = True

    ui.display_game_end(game.players)

