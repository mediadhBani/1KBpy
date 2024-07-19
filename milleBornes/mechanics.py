from milleBornes.ui import UI
from .cards import Card, CardShoe, State
from .players import Player, Status
from .rules import Rule, BadMove


class Game:
    def __init__(self, ui: UI):
        self.deck = CardShoe()
        self.turn = -1
        self.turn_end = True
        self.ui = ui

    def render_state(self):
        # rafraichir affichage
        self.ui.refresh_display()
        # affichage main joueur courante
        self.ui.display_hand(self.current_player)
        # affichage tableaux des joueurs
        self.ui.display_tableaus(self.players, self.turn)
        # affichage message évènement
        self.ui.display_message()

    def prompt_action(self) -> int:
        self.card_idx, self.target_idx = self.ui.prompt_action()
        return self.card_idx

    
    def is_over(self) -> bool:
        return self.current_player.score == Rule.WINNING_DISTANCE or not self.deck.has_distances()

    def start_turn(self) -> Player:
        self.turn = (self.turn + self.turn_end) % self.number_players
        self.current_player = self.players[self.turn]

        if self.turn_end:
            self.current_player.hand.append(self.deck.draw())
            self.turn_end = False

        return self.current_player

    def do_action(self):
        if self.target_idx != -1:
            if self.target_idx is None:
                self.target_idx = self.turn
            if not (
                (card := self.current_player.hand[self.card_idx]).is_hazard() ^ 
                ((target := self.players[self.target_idx]) is self.current_player)
            ):
                raise BadMove("Vous ne pouvez pas vous attaquer à vous même.")

            self.play(target, card)


        self.current_player.hand.pop(self.card_idx)
        self.turn_end = True

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

    def prepare(self):
        self.number_players = self.ui.prompt_number_players()

        self.players = [
            Player(
                name=f"J{i}", hazards=State.LIGHT, hand=self.deck.deal()
            ) for i in range(self.number_players)
        ]
        self.current_player = self.players[0]

    def conclude(self):
        self.ui.display_game_end(self.players)

    def pass_error(self, exc: Exception):
        self.ui.alert = exc
        
