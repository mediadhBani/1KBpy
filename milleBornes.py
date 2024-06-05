# pyright: strict

from abc import ABC, abstractmethod
from enum import IntEnum, IntFlag, auto
from dataclasses import dataclass, field
from typing import Iterable, Self, Any

class Rule(IntEnum):
    WINNING_DISTANCE: int = 1000
    SPEED_LIMIT = 50
    MAX_USE_200 = 2

class State(IntFlag):
    RED_LIGHT = auto()
    SPEED_LIMIT = auto()
    OUT_OF_FUEL = auto()
    FLAT_TIRE = auto()
    ACCIDENT = auto()

    def is_singular(self) -> bool:
        """Verifier que la situation donnée n'est pas une combinaison de plusieurs situations"""
        return self.bit_count() == 1
    

@dataclass(frozen=True, slots=True)
class Card(ABC):
    value: Any
    
    @classmethod
    @abstractmethod
    def get_content(cls) -> dict[Any, int]:
        """Renvoie un dictionnaire de cartes de la classe courante et leur nombre dans le jeu."""
        pass

    @classmethod
    def generate_all(cls) -> list[Self]:
        cards: list[Self] = []
        return sum((v * [cls(k)] for k, v in cls.get_content().items()), cards)

class Distance(Card):
    @classmethod
    def get_content(cls) -> dict[int, int]:
        return {
        25: 10,
        50: 10,
        75: 10,
        100: 12,
        200: 4,
    }

    def __str__(self) -> str:
        return f"{self.value} bornes"
        
class Hazard(Card):
    value: State

    @classmethod
    def get_content(cls) -> dict[State, int]:
        return {
            State.RED_LIGHT: 5,
            State.SPEED_LIMIT: 4,
            State.OUT_OF_FUEL: 3,
            State.FLAT_TIRE: 3,
            State.ACCIDENT: 3,
        }

    def __str__(self) -> str:
        match self.value:
            case State.RED_LIGHT: return "Feu rouge"
            case State.SPEED_LIMIT: return "Limite de vitesse (50 bornes/tour)"
            case State.OUT_OF_FUEL: return "Panne d'essence"
            case State.FLAT_TIRE: return "Crevaison"
            case State.ACCIDENT: return "Accident"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self.value!r}")
    
class Remedy(Card):
    value: State

    @classmethod
    def get_content(cls) -> dict[State, int]:
        return {
            State.RED_LIGHT: 14,
            State.SPEED_LIMIT: 6,
            State.OUT_OF_FUEL: 6,
            State.FLAT_TIRE: 6,
            State.ACCIDENT: 6,
        }       

    def __str__(self) -> str:
        match self.value:
            case State.RED_LIGHT: return "Feu vert"
            case State.SPEED_LIMIT: return "Fin de limite de vitesse"
            case State.OUT_OF_FUEL: return "Essence"
            case State.FLAT_TIRE: return "Roue de Secours"
            case State.ACCIDENT: return "Réparations"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self.value!r}")

class Safety(Card):
    value: State

    @classmethod
    def get_content(cls) -> dict[State, int]:
        return {
            State.RED_LIGHT | State.SPEED_LIMIT: 1,
            State.OUT_OF_FUEL: 1,
            State.FLAT_TIRE: 1,
            State.ACCIDENT: 1,
        }       

    def __str__(self) -> str:
        match self.value:
            case State.RED_LIGHT | State.SPEED_LIMIT: return "Véhicule prioritaire"
            case State.OUT_OF_FUEL: return "Citerne d'essence"
            case State.FLAT_TIRE: return "Increvable"
            case State.ACCIDENT: return "As du volant"

        if self.value is State.RED_LIGHT | State.SPEED_LIMIT:
            return "Véhicule prioritaire"

@dataclass
class Player:
    score: int = 0
    count200: int = 0
    hazards: State = State(0)
    safeties: State = State(0)
    hand: list[Card] = field(default_factory=list)

    def can_get(self, card: Card) -> bool:
        """Vérifier si le joueur courant peut recevoir les effets de la carte considérée."""
        match card:
            case Safety():
                return True
            case Remedy():
                return self.hazards & card.value is not State(0)
            case Distance():
                return self.hazards & ~State.SPEED_LIMIT is State(0) \
                    and (card.value <= Rule.SPEED_LIMIT or not State.SPEED_LIMIT in self.hazards) \
                    and self.score + card.value <= Rule.WINNING_DISTANCE \
                    and (card.value != 200 or self.count200 < Rule.MAX_USE_200)
            case Hazard():
                if card.value is State.SPEED_LIMIT:
                    return State.SPEED_LIMIT not in self.hazards | self.safeties
                return self.hazards & ~State.SPEED_LIMIT is State(0) and card.value not in self.safeties
            case _:
                raise NotImplemented

def validate_input(prompt: str, allowed_values: Iterable[int]) -> int:
    while True:
        try:
            if (value := int(input(prompt))) in allowed_values:
                return value
            raise ValueError
        except ValueError:
            print("\x1B[A\x1B[KSaisie invalide.", end=" ")

    
if __name__ == "__main__":
    from random import shuffle

    # instanciation de la pioche
    deck: list[Card] = []
    for card_class in [Distance, Hazard, Remedy, Safety]:
        deck.extend(card_class.generate_all())
    shuffle(deck)

    # instanciation des joueurs
    number_players: int = 2
    players = [Player(hazards=State.RED_LIGHT) for _ in range(number_players)]
    for player in players:
        player.hand = [deck.pop() for _ in range(6)]

    # compteurs et drapeau
    remaining_distances: int = sum(type(card) is Distance for card in deck)
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
            remaining_distances -= type(card) is Distance
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
                            remaining_distances -= (type(c) is Distance)
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

        if remaining_distances == 0:
            winner = max(players, key=lambda p: p.score)
            print(f"Le joueur J{players.index(winner)} a le score le plus élevé avec {winner.score} bornes !")
            break

        turns += 1
        turn_end = True

    # tableau des scores
    for rank, player in enumerate(sorted(players, key=lambda p: p.score, reverse=True)):
        print(f"#{rank+1} J{players.index(player)} {player.score: >4}")

