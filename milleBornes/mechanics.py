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
        # rafraichir affichage
        self.ui.refresh_display()
        # affichage main joueur courant
        self.ui.display_hand(self.current_player)
        # affichage tableaux des joueurs
        self.ui.display_tableaus(self.players, self.turn % self.number_players)
        # affichage message évènement
        self.ui.display_message()


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

