from .players import Player
from .cards import *
from .ui import UI

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

    def play(self, player: Player, card: Card):
        match card:
            case Distance():
                player.score += card.value
                player.count200 += (card.value == 200)
            case Remedy():
                player.hazards &= ~card.value
            case Safety():
                player.hazards &= ~card.value
                player.safeties |= card.value
                self.turn -= 1
                print("rejouez.")

            case _:
                raise ValueError(f"The given case should have been handled elsewhere. Received: {card!r}")

