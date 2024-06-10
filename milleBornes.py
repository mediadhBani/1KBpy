# pyright: strict

from milleBornes.players import *
from milleBornes.ui import CLI

if __name__ == "__main__":
    ui = CLI()
    deck = CardShoe()  # création de la pioche

    number_players = ui.prompt_number_players()
    players = [
        Player(name=f"J{i}",
               hazards=State.RED_LIGHT,
               hand=deck.deal()
        ) for i in range(number_players)
    ]
        
    # compteurs et drapeau
    turns: int = 0
    turn_end = True
    player = players[0]

    while True:
        if turn_end:
            player = players[turns % number_players]
            card = deck.draw()
            player.hand.append(card)
            turn_end = False

        # montrer l'interface du jeu
        print()
        ui.display_hand(player)
        ui.display_tableau(player)

        # jouer une carte
        card_idx = ui.prompt_choice_card()
        if card_idx < 0:
            player.hand.pop(card_idx)
            turn_end = True
            turns += 1
            continue

        # choix de la cible
        if type(card := player.hand[card_idx]) is Hazard:
            target_idx = ui.prompt_choice_target(player, players)
            target = players[target_idx]
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
            case Distance():
                target.score += card.value
                target.count200 += (card.value == 200)
            case Remedy():
                target.hazards &= ~card.value
            case Safety():
                target.hazards &= ~card.value
                target.safeties |= card.value
                turns -= 1
                print("rejouez.")
            case Hazard():
                for i, c in enumerate(target.hand):
                    if type(c) is Safety and card.value & c.value != State(0):
                        print("Coup fourré !")
                        target.hand.pop(i)
                        target.safeties |= c.value
                        card = deck.draw()
                        target.hand.append(card)
                        turns = players.index(target) - 1
                        break
                else:
                    target.hazards |= card.value

        # la carte jouée est défaussée
        player.hand.pop(card_idx)
        turns += 1
        turn_end = True

        # check end of game
        if player.score == Rule.WINNING_DISTANCE or not deck.has_distances():
            break

    ui.display_ranking(players)
