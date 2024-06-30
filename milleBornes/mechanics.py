from .cards import Card, CardShoe, State
from .players import Player, Status
from .rules import Rule
from .ui import CLI


class Game:
    def __init__(self, number_players: int):
        self.number_players = number_players
        self.deck = CardShoe()
        self.turn = -1
        self.turn_end = True
        self.ui = CLI()
        self.players = [
            Player(name=f"J{i}",
                   hazards=State.LIGHT,
                   hand=self.deck.deal()
            ) for i in range(self.number_players)
        ]
        self.current_player = self.players[0]

    def render_state(self):
        # effacer écran
        print("\x1B[2J\x1B[H", end="")

        # panneau gauche
        self.ui.display_hand(self.current_player)
        
        # panneau droite
        for i, player in enumerate(self.players):
            print(f"\x1B[{i+1};35H  {i}: ", end="")
            self.ui.display_tableau(player)

        print(f"\x1B[{self.players.index(self.current_player) + 1};35H>")
        print("\x1B[6;35H\x1B[K\x1B[33m", self.ui.errmsg, end="\x1B[m\x1B[999;H")
        self.ui.errmsg = ""


    def is_over(self) -> bool:
        return self.current_player.score == Rule.WINNING_DISTANCE or not self.deck.has_distances()

    def pick_player(self) -> Player:
        self.turn += self.turn_end
        self.current_player = self.players[self.turn % self.number_players]

        if self.turn_end:
            self.current_player.hand.append(self.deck.draw())
            self.turn_end = False

        return self.current_player

    def play(self, player: Player, card: Card):
        player <<= card
        
        if player.status is Status.SAFETY:
            print("__Rejouez.__")
            self.turn -= 1
        elif player.status is Status.COUNTER_TRHUST:
            print("__Coup fourré !__")
            player.hand.append(self.deck.draw())
            self.turn = self.players.index(player) - 1

        player.status = Status.OK
        self.turn_end = True

