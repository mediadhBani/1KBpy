from .cards import Card, CardShoe, State
from .players import Player, Status
from .rules import Rule, BadMove


class Game:
    def __init__(self, ui: type):
        self.deck = CardShoe()
        self.turn = -1
        self.turn_end = True
        self.ui = ui()

    def render_state(self):
        # rafraichir affichage
        self.ui.refresh_display()
        # affichage main joueur courante
        self.ui.display_hand(self.current_player)
        # affichage tableaux des joueurs
        self.ui.display_tableaus(self.players, self.turn % self.number_players)
        # affichage message évènement
        self.ui.display_message()

    def prompt_action(self) -> int:
        self.card_idx = self.ui.prompt_choice_card()
        return self.card_idx

    

    def is_over(self) -> bool:
        return self.current_player.score == Rule.WINNING_DISTANCE or not self.deck.has_distances()

    def start_turn(self) -> Player:
        self.turn += self.turn_end
        self.current_player = self.players[self.turn % self.number_players]

        if self.turn_end:
            self.current_player.hand.append(self.deck.draw())
            self.turn_end = False

        return self.current_player

    def do_action(self):
        if self.card_idx >= 0:
            if (card := self.current_player.hand[self.card_idx]).is_hazard():
                target_idx = self.ui.prompt_choice_target(self.current_player, self.players)
                if self.current_player is (target := self.players[target_idx]):
                    raise BadMove("Vous ne pouvez pas vous attaquer à vous même.")
            else:
                target = self.current_player
                
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
