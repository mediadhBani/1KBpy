from abc import ABC, abstractmethod
from sys import exit
from .players import Player
from .cards import Card, Distance, Hazard, Remedy, Rule, Safety, State
# from .mechanics import Game

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
        self.number_players: int = 0
        self.errmsg: str = ""

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

    def display_ui(self, game):
        # effacer écran
        print("\x1B[2J\x1B[H", end="")

        # panneau gauche
        current_player = game.pick_player()
        self.display_hand(current_player)
        
        # panneau droite
        for i, player in enumerate(game.players):
            print(f"\x1B[{i+1};35H  {i}: ", end="")
            self.display_tableau(player)

        print(f"\x1B[{game.players.index(current_player) + 1};35H>")
        print("\x1B[6;35H\x1B[K\x1B[33m", self.errmsg, end="\x1B[m\x1B[999;H")
        
        

    def display_hand(self, player: Player):
        for i, card in enumerate(player.hand):
            print(f"{i}: {self.COLOR[type(card)]}{card}\x1B[m")

    def display_tableau(self, player: Player):
        # affichage nom du joueur
        print(f"{player.name.upper():>3.3} | ", end="")

        # afficher nombre de cartes 200 Bornes jouées
        if player.count200 == Rule.MAX_USE_200:
            print("\x1B[31m", end="")      
        print(f"{player.count200}×200\x1B[m | ", end="")

        # affichage distance
        print(f"{player.score:>4}/{Rule.WINNING_DISTANCE} | ", end="\x1B[s")

        # affichage états
        fmt = "\x1B[{}C\x1B[{}m{}"
        offset, shorthand = 0, ""
        for state in State:
            if state is State.SPEED:
                offset, shorthand = -1, "LIM"
            elif state is State.LIGHT:
                offset, shorthand = 5, "FEU"
            elif state is State.FUEL:
                offset, shorthand = 9, "ESS"
            elif state is State.TIRE:
                offset, shorthand = 13, "ROU"
            elif state is State.ACCIDENT:
                offset, shorthand = 17, "ACC"
            else:
                raise ValueError("shorthand error")


            color = 2
            if state in player.safeties:
                color = 32
            elif state in player.hazards:
                color = 31
                

            print(fmt.format(offset, color, shorthand), end="\x1B[m\x1B[u")
        print()


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
            

    def prompt_choice_target(self, attacker: Player, players: list[Player]) -> int:
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

    def display_game_end(self, players: list[Player]):
        players = sorted(players, key=lambda p: p.score, reverse=True)
        print(f"Le gagnant est {players[0].name}.")
        for rank, player in enumerate(players):
            print(f"#{rank+1} {player.name: <8} {player.score: >4}")


