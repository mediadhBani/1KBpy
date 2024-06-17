# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.players import *
from milleBornes.ui import CLI


if __name__ == "__main__":
    ui = CLI()
    game = Game(ui.prompt_number_players())

    while True:
        try:
            player = game.pick_player()

            # montrer l'interface du jeu
            print()
            ui.display_hand(player)
            ui.display_tableau(player)

            # choisir une carte
            card_idx = ui.prompt_choice_card()

            # si le joueur défausse
            if card_idx < 0:
                player.hand.pop(card_idx)
                game.turn_end = True
                continue

            # choisir la cible
            if type(card := player.hand[card_idx]) is Hazard:
                target_idx = ui.prompt_choice_target(player, game.players)
                target = game.players[target_idx]
                if player is target:
                    continue
            else:
                target = player

            # la cible subit les effets de la carte
            game.play(target, card)

            # la carte jouée est défaussée
            player.hand.pop(card_idx)
            game.turn_end = True

            # check end of game
            if player.score == Rule.WINNING_DISTANCE or not game.deck.has_distances():
                break

        # le joueur quitte avec les raccourcis ^C ou ^Z ou avec 
        except (EOFError, SystemExit):
            break
        except ValueError as exc:
            print(exc)
            continue

    ui.display_game_end(game.players)

