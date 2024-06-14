# pyright: strict

from milleBornes.mechanics import Game
from milleBornes.players import *
from milleBornes.ui import CLI


if __name__ == "__main__":
    game = Game(CLI())

    while True:
        try:
            player = game.pick_player()

            # montrer l'interface du jeu
            print()
            game.ui.display_hand(player)
            game.ui.display_tableau(player)

            # choisir une carte
            card_idx = game.ui.prompt_choice_card()

            # si le joueur défausse
            if card_idx < 0:
                player.hand.pop(card_idx)
                game.turn_end = True
                continue

            # choisir la cible
            if type(card := player.hand[card_idx]) is Hazard:
                target_idx = game.ui.prompt_choice_target(player, game.players)
                target = game.players[target_idx]
                if player is target:
                    continue
            else:
                target = player

            # vérifier que la carte est jouable
            if not target.can_get(card):
                print("Vous ne pouvez pas jouer cette carte.")
                continue

            # appliquer les effets de la carte sur la cible
            match card:
                case Distance() | Remedy() | Safety():
                    game.play(target, card)
                case Hazard():
                    for i, c in enumerate(target.hand):
                        if type(c) is Safety and card.value & c.value != State(0):
                            print("Coup fourré !")
                            target.hand.pop(i)
                            target.safeties |= c.value
                            card = game.deck.draw()
                            target.hand.append(card)
                            turns = game.players.index(target) - 1
                            break
                    else:
                        target.hazards |= card.value

            # la carte jouée est défaussée
            player.hand.pop(card_idx)
            game.turn_end = True

            # check end of game
            if player.score == Rule.WINNING_DISTANCE or not game.deck.has_distances():
                game.ui.display_game_end(game.players)
                break

        # le joueur quitte avec les raccourcis ^C ou ^Z ou avec 
        except (EOFError, InterruptedError, SystemExit):
            break


