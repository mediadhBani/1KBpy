from milleBornes.ui import UI
from .cards import Card, CardShoe, State
from .players import Player
from .rules import Rule, BadMove, SafetyUse, CounterThrust


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

    def prompt_action(self):
        self.card_idx, self.target_idx = self.ui.prompt_action()
        card = self.current_player.hand[self.card_idx]

        if self.target_idx is not None and self.target_idx >= self.number_players:
            raise BadMove(f"Il n'y a que {self.number_players} joueurs ou joueuses à viser.")

        if card.is_hazard() and self.target_idx == self.turn:
            raise BadMove("Vous ne pouvez pas vous attaquer à vous même.")

        if card.is_hazard() and self.target_idx is None and self.number_players > 2:
            raise BadMove("Veuillez préciser l'adversaire à attaquer.")

        if not card.is_hazard() and self.target_idx not in {-1, None, self.turn}:
            raise BadMove("Vous ne pouvez pas aider vos adversaires.")

        if self.target_idx is None:
            self.target_idx = self.number_players - self.turn - 1 if card.is_hazard() else self.turn


    def is_over(self) -> bool:
        return self.current_player.score == Rule.WINNING_DISTANCE or not self.deck.has_distances()

    def start_turn(self):
        self.turn = (self.turn + self.turn_end) % self.number_players
        self.current_player = self.players[self.turn]

        if self.turn_end:
            self.current_player.hand.append(self.deck.draw())
            self.turn_end = False


    def do_action(self):
        if self.target_idx != -1:
            card = self.current_player.hand[self.card_idx]
            target = self.players[self.target_idx]
            self.play(target, card)

        self.current_player.hand.pop(self.card_idx)
        self.turn_end = True

    def play(self, player: Player, card: Card):
        try:
            player.take(card)
        except SafetyUse as exc:
            self.ui.alert = exc
            self.turn -= 1
        except CounterThrust as exc:
            self.ui.alert = exc
            player.hand.append(self.deck.draw())
            self.turn = self.players.index(player) - 1
            

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
        
