# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.ui import CLI
from milleBornes.rules import BadMove, Rule


if __name__ == "__main__":
    ui = CLI()
    game = Game(ui.prompt_number_players())

    while True:
        player = game.pick_player()
        ui.display_ui(game)
        ui.errmsg = ""

        try:
            card_idx = ui.prompt_choice_card()

            if (card := player.hand[card_idx]).is_hazard():
                target_idx = ui.prompt_choice_target(player, game.players)
                target = game.players[target_idx]
                if player is target:
                    continue
            else:
                target = player
        except (EOFError, SystemExit):
            break

        # si le joueur défausse
        if card_idx < 0:
            player.hand.pop(card_idx)
            game.turn_end = True
            continue

        # la cible subit les effets de la carte
        try:
            game.play(target, card)
        except BadMove as exc:
            ui.errmsg = str(exc)
            continue

        # la carte jouée est défaussée
        player.hand.pop(card_idx)
        game.turn_end = True

        # check end of game
        if player.score == Rule.WINNING_DISTANCE or not game.deck.has_distances():
            break

    ui.display_game_end(game.players)

