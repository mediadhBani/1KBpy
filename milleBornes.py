# pyright: strict

from milleBornes.players import *

if __name__ == "__main__":
    # instanciation de la pioche
    deck = CardShoe()

    # instanciation des joueurs
    number_players: int = 2
    players = [Player(hazards=State.RED_LIGHT) for _ in range(number_players)]
    for player in players:
        player.hand = [deck.pop() for _ in range(6)]

    # compteurs et drapeau
    turns: int = 0
    turn_end = True
    player = players[0]

    def card_color(card: Card):
        match card:
            case Hazard(): return "\x1B[31m"
            case Remedy(): return "\x1B[34m"
            case Safety(): return "\x1B[32m"
            case _: return "\x1B[0m"

    while True:
        if turn_end:
            player = players[turns % number_players]
            card = deck.pop()
            player.hand.append(card)
            turn_end = False

        # montrer l'interface du jeu
        print()
        for i, c in enumerate(player.hand):
            print(f"{i}: {card_color(c)}{c}\x1B[m")
        print("J", turns % number_players, sep="", end=" | ")                     # joueur courant
        print(f"{player.score}/{Rule.WINNING_DISTANCE} bornes", end="\x1B[m | ")  # distance parcourue
        if player.safeties:
            print("\x1B[32m", end="")
            print(*map(Safety, player.safeties & ~State.SPEED_LIMIT), sep=", ", end="\x1B[m | ")       # bottes
        if player.hazards:
            print("\x1B[31m", end="")
            print(*map(Hazard, player.hazards), sep=", ", end="\x1B[m\n")         # attaques subies
        else:
            print("La voie est libre")

        # valider la saisie
        if (choice := input("[q = quitter] [n = jouer carte n] [-n = retirer carte n] ")) \
            not in {"q", "-0", "-1", "-2", "-3", "-4", "-5", "-6", "0", "1", "2", "3", "4", "5", "6"}:
            print("Saisie invalide")
            continue

        # quitter la partie si "q"
        if choice == "q":
            break

        # aplliquer les effets
        card_idx = abs(int(choice))
        if choice[0] != "-":
            card = player.hand[card_idx]

            if type(card) is Hazard:
                if (choice := input("[r = retour] [n = cibler joueur n] ")) == "r":
                    continue
                elif choice not in set(map(str, range(number_players))) - set(str(turns % number_players)):
                    print("Saisie invalide")
                    continue
                target = players[int(choice)]
            else:
                target = player

            if not target.can_get(card):
                print("Vous ne pouvez pas jouer cette carte.")
                continue
            
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
                            card = deck.pop()
                            target.hand.append(card)
                            turns = players.index(target) - 1
                            break
                    else:
                        target.hazards |= card.value
                case _:
                    raise NotImplemented

        # la carte jouée est défaussée
        player.hand.pop(card_idx)

        # check end of game
        if player.score == Rule.WINNING_DISTANCE:
            print(f"Le joueur J{players.index(player)} a gagné !")
            break

        if not deck.has_distances():
            winner = max(players, key=lambda p: p.score)
            print(f"Le joueur J{players.index(winner)} a le score le plus élevé avec {winner.score} bornes !")
            break

        turns += 1
        turn_end = True

    # tableau des scores
    for rank, player in enumerate(sorted(players, key=lambda p: p.score, reverse=True)):
        print(f"#{rank+1} J{players.index(player)} {player.score: >4}")

