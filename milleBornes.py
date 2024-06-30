# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI
from milleBornes.rules import BadMove


if __name__ == "__main__":
    ui = CLI()
    game = Game(ui.prompt_number_players())

    while True:
        player = game.pick_player()
        game.render_state()
        # game.prompt_action()
        # game.do_action()
        # if game.is_over():
        #     break
        
        try:
            card_idx = ui.prompt_choice_card()
        except (EOFError, SystemExit):
            break


        # si le joueur ne défausse pas
        if card_idx >= 0:
            try:
                if (card := player.hand[card_idx]).is_hazard():
                    target_idx = ui.prompt_choice_target(player, game.players)
                    if player is (target := game.players[target_idx]):
                        raise BadMove("Vous ne pouvez pas vous attaquer à vous même.")
                else:
                    target = player

                game.play(target, card)
            except BadMove as exc:
                game.ui.errmsg = str(exc)
                continue

        # la carte jouée est défaussée
        player.hand.pop(card_idx)
        game.turn_end = True

        # check end of game
        if game.is_over():
            break

    ui.display_game_end(game.players)

