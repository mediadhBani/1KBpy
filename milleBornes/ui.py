from abc import ABC, abstractmethod
from sys import exit
from .players import Player
from .cards import Card, State, Distance, Hazard, Remedy, Rule, Safety


class UI(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    def input(self, prompt: str, options: set[str], help="") -> str:
        prompt = "\x1B[K" + prompt + "\x1B[s"
        help = "\x1B[3m" + help + "\x1B[u\x1B[A\x1B[K"
        while True:
            try:
                if not (ans := input(prompt)) in options:
                    raise ValueError

                if prompt == help:
                    print()

                return ans
            except ValueError:
                prompt = help
                continue

class CLI(UI):
    COLOR: dict[type[Card], str] = {
        Distance: "\x1B[39m",
        Hazard: "\x1B[31m",
        Remedy: "\x1B[34m",
        Safety: "\x1B[32m",
    }

    def __init__(self):
        self.number_players = 0

    def prompt_number_players(self) -> int:
        ans = self.input(
            "Combien de joueurs ? ",
            {"0", "2", "3", "4"},
            "0 pour quitter ou 2 à 4 pour jouer."
        )
        
        self.number_players = int(ans)
        if self.number_players == 0:
            exit(0)

        return self.number_players

    def display_hand(self, player: Player):
        for i, card in enumerate(player.hand):
            print(f"{i}: {self.COLOR[type(card)]}{card}\x1B[m")

    def display_tableau(self, player: Player):
        # affichage nom du joueur
        print(player.name, end=" | ")

        # affichage distance
        print(f"{player.score}/{Rule.WINNING_DISTANCE}", end=" | ")

        # affichage bottes
        states = map(Safety, player.safeties & ~State.SPEED_LIMIT)
        states = map((self.COLOR[Safety] + "{}\x1B[m").format, states)
        print(", ".join(states) or "aucune botte", end=" | ")

        # affichage attaque
        states = map(Hazard, player.hazards)
        states = map((self.COLOR[Hazard] + "{}\x1B[m").format, states)
        print(", ".join(states) or "La voie est libre.")


    def prompt_choice_card(self) -> int:
        card_range = set(map(str, range(Rule.FIRST_DEAL + 1)))
        ans = self.input(
            "Quelle carte jouer ? ",
            {"q"} | card_range | set(map("-".__add__, card_range)),
            "q : quitter\tn: jouer la carte n\t-n: défausser la carte n"
        )

        if ans == "q":
            exit()
        if ans in card_range:
            return int(ans)
        else:
            return -int(ans) - Rule.FIRST_DEAL - 1
            

    def prompt_choice_target(self, attacker: Player, players: list[Player]):
        if len(players) == 2:
            return 1 - players.index(attacker)

        options: set[str] = set(str(i) for i in range(len(players)) if players[i] is not attacker)

        ans = self.input(
            "Qui attaquer ? ",
            {"a", "q"} | options,
            "a pour annuler, q pour quitter, sinon choisir parmi " + ", ".join(options)
        )

        if ans == "a":
            return players.index(attacker)

        if ans == "q":
            exit()

        return int(ans)

    def display_ranking(self, players: list[Player]):
        players = sorted(players, key=lambda p: p.score)
        print(f"Le gagnant est {players[-1].name}")
        for rank, player in enumerate(sorted(players, key=lambda p: p.score, reverse=True)):
            print(f"#{rank+1} J{players.index(player)} {player.score: >4}")


