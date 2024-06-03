# pyright: strict

from abc import ABC, abstractmethod
from enum import IntFlag, auto
from dataclasses import dataclass, field
from typing import Self

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
class Card[T: (int, State)](ABC):
    value: T
    
    def __rmul__(self, other: int) -> list[Self]:
        """Fonction d'appoint pour dupliquer une carte plusieurs fois"""
        return [self for _ in range(other)]

    @abstractmethod
    def __post_init__(self):
        pass

class Distance(Card[int]):
    ALLOWED_VALUES: list[int] = [25, 50, 75, 100, 200]
    SPEED_LIMIT: int = 50

    def __post_init__(self):
        assert type(self.value) is int and self.value in self.ALLOWED_VALUES, \
            f"Mauvaise initialisation de la carte Bornes. Valeur reçue : {self.value!r}"

    def __str__(self) -> str:
        return f"{self.value} bornes"
        
class Hazard(Card[State]):
    def __post_init__(self):
        assert type(self.value) is State and self.value.is_singular(), \
            f"Mauvaise initialisation de la carte Attaque. Valeur reçue : {self.value!r}"

    def __str__(self) -> str:
        match self.value:
            case State.RED_LIGHT: return "Feu rouge"
            case State.SPEED_LIMIT: return "Limite de vitesse (50 bornes/tour)"
            case State.OUT_OF_FUEL: return "Panne d'essence"
            case State.FLAT_TIRE: return "Crevaison"
            case State.ACCIDENT: return "Accident"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self.value!r}")
    
class Remedy(Card[State]):
    def __post_init__(self):
        assert type(self.value) is State and self.value.is_singular(), \
            f"Mauvaise initialisation de la carte Parade. Valeur reçue : {self.value!r}"

    def __str__(self) -> str:
        match self.value:
            case State.RED_LIGHT: return "Feu vert"
            case State.SPEED_LIMIT: return "Fin de limite de vitesse"
            case State.OUT_OF_FUEL: return "Essence"
            case State.FLAT_TIRE: return "Roue de Secours"
            case State.ACCIDENT: return "Réparations"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self.value!r}")

class Safety(Card[State]):
    ALLOWED_VALUES: list[State] = [State(s) for s in [1|2, 4, 8, 16]]

    def __post_init__(self):
        assert type(self.value) is State and self.value in self.ALLOWED_VALUES, \
            f"Mauvaise initialisation de la carte Botte. Valeur reçue : {self.value!r}"

    def __str__(self) -> str:
        if self.value == State.RED_LIGHT | State.SPEED_LIMIT:
            return "Véhicule prioritaire"

        match self.value:
            case State.OUT_OF_FUEL: return "Citerne d'essence"
            case State.FLAT_TIRE: return "Increvable"
            case State.ACCIDENT: return "As du volant"
            case _:
                raise ValueError(f"Carte Corrompue ! Valeur reçue : {self.value!r}")

@dataclass
class Player:
    score: int = 0
    count200: int = 0
    hazards: State = State(0)
    safeties: State = State(0)
    hand: list[Card[int | State]] = field(default_factory=list)



def validate_input(prompt: str, upperbound: int) -> int:
    while True:
        try:
            if 0 <= (value := int(input(prompt))) < upperbound:
                return value
            raise ValueError
        except ValueError:
            print("\x1B[A\x1B[KSaisie invalide.", end=" ")

    
if __name__ == "__main__":
    from random import shuffle
    type Card_ = Card[int | State]

    deck: list[Card_] = [Safety(State(s)) for s in Safety.ALLOWED_VALUES]
    
    for n, s in zip([5, 4, 3, 3, 3], State):
        deck.extend(n * Hazard(s))

    for n, s in zip([14, 6, 6, 6, 6], State):
        deck.extend(n * Remedy(s))

    for n, d in zip([10, 10, 10, 12, 4], Distance.ALLOWED_VALUES):
        deck.extend(n * Distance(d))

    shuffle(deck)

    players = [Player(hazards=State.RED_LIGHT) for _ in range(2)]
    nbPlayers = len(players)

    for i, p in enumerate(players):
        p.hand = [deck.pop() for _ in range(6)]


    DISTANCE_WIN: int = 1000
    remaining_distances: int = 46
    turns = 0

    while True:
        card, player = deck.pop(), players[turns % nbPlayers]
        remaining_distances -= type(card) is Distance

        # montrer main en jeu
        player.hand.append(card)
        print("\n".join(f"{i}: {c}" for i, c in enumerate(player.hand)))

        # montrer stats
        print(f"{player.score}/{DISTANCE_WIN} bornes", end=" | ")
        if player.safeties:
            print("\x1B[32m", end="")
            print(*map(Safety, player.safeties), sep=", ", end="\x1B[m | ")
        if player.hazards:
            print("\x1B[31m", end="")
            print(*map(Hazard, player.hazards), sep=", ", end="\x1B[m\n")
        else:
            print("La voie est libre")


        card_idx = validate_input("Jouer une carte en saisissant l'indice correspondant : ", 7)
        match (card := player.hand[card_idx]):
            case Distance():
                if (not player.hazards or player.hazards is State.SPEED_LIMIT and card.value <= Distance.SPEED_LIMIT) \
                and player.score + card.value <= DISTANCE_WIN:
                    player.score += card.value
                else:
                    print("Vous ne pouvez pas jouer cette carte.")
                    continue

            case Hazard():
                target = players[validate_input("Quel joueur attaquer ?", len(players))]
                if player is not target \
                and card.value not in target.hazards \
                and card.value not in target.safeties:
                    ...
                else:
                    print("Vous ne pouvez pas attaquer ce joueur.")
                    continue

            case Remedy():
                if player.hazards & card.value:
                    player.hazards &= ~card.value
                else:
                    print("Cette Parade ne change rien à votre situation !")
                    continue

            case Safety():
                player.safeties |= card.value
                player.hazards &= ~card.value

        player.hand.pop(card_idx)

        # check end of game
        if player.score == DISTANCE_WIN:
            print(f"Le joueur J{players.index(player)} a gagné !")
            break

        if remaining_distances == 0:
            winner = max(players, key=lambda p: p.score)
            print(f"Le joueur J{players.index(winner)} a le score le plus élevé avec {winner.score} bornes !")
            break

        turns += 1

