# pyright: strict

from milleBornes.players import *
from milleBornes.ui import CLI, UI

class Game:
    def __init__(self, ui: UI):
        self.ui = ui
        self.number_players = ui.prompt_number_players()
        self.deck = CardShoe()
        self.turn = -1
        self.turn_end = True

        self.players = [
            Player(name=f"J{i}",
                   hazards=State.RED_LIGHT,
                   hand=self.deck.deal()
            ) for i in range(self.number_players)
        ]

    def pick_player(self) -> Player:
        self.turn += self.turn_end
        player = self.players[self.turn % self.number_players]

        if self.turn_end:
            player.hand.append(self.deck.draw())
            self.turn_end = False
        
        return player



if __name__ == "__main__":
    game = Game(CLI())
        
    while True:
        player = game.pick_player()

        # montrer l'interface du jeu
        print()
        game.ui.display_hand(player)
        game.ui.display_tableau(player)

        # jouer une carte
        card_idx = game.ui.prompt_choice_card()
        if card_idx < 0:
            player.hand.pop(card_idx)
            game.turn_end = True
            continue

        # choix de la cible
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
            case Distance():
                target.score += card.value
                target.count200 += (card.value == 200)
            case Remedy():
                target.hazards &= ~card.value
            case Safety():
                target.hazards &= ~card.value
                target.safeties |= card.value
                game.turn -= 1
                print("rejouez.")
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
            break

    game.ui.display_game_end(game.players)

