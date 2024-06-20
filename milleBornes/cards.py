from abc import ABC, abstractmethod
from random import shuffle
from dataclasses import dataclass
from enum import Flag, auto
from typing import Any, Self

from .rules import Rule


class State(Flag):
    SPEED = auto()
    LIGHT = auto()
    FUEL = auto()
    TIRE = auto()
    ACCIDENT = auto()
    PRIORITY = SPEED | LIGHT

    def ignore_speed(self):
        return self & ~self.SPEED

    def iter_safety(self):
        if self.PRIORITY in self:
            yield self.PRIORITY

        for s in ~self.PRIORITY & self:
            yield s


@dataclass(frozen=True, slots=True)
class BaseCard(ABC):
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

class Distance(BaseCard):
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
        
class Hazard(BaseCard):
    value: State

    @classmethod
    def get_content(cls) -> dict[State, int]:
        return {
            State.LIGHT: 5,
            State.SPEED: 4,
            State.FUEL: 3,
            State.TIRE: 3,
            State.ACCIDENT: 3,
        }

    def __str__(self) -> str:
        match self.value:
            case State.LIGHT: return "Feu rouge"
            case State.SPEED: return "Limite de vitesse"
            case State.FUEL: return "Panne d'essence"
            case State.TIRE: return "Crevaison"
            case State.ACCIDENT: return "Accident"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self!r}")
    
class Remedy(BaseCard):
    value: State

    @classmethod
    def get_content(cls) -> dict[State, int]:
        return {
            State.LIGHT: 14,
            State.SPEED: 6,
            State.FUEL: 6,
            State.TIRE: 6,
            State.ACCIDENT: 6,
        }       

    def __str__(self) -> str:
        match self.value:
            case State.LIGHT: return "Feu vert"
            case State.SPEED: return "Fin de limite de vitesse"
            case State.FUEL: return "Essence"
            case State.TIRE: return "Roue de Secours"
            case State.ACCIDENT: return "Réparations"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self!r}")

class Safety(BaseCard):
    value: State

    @classmethod
    def get_content(cls) -> dict[State, int]:
        return {
            State.PRIORITY: 1,
            State.FUEL: 1,
            State.TIRE: 1,
            State.ACCIDENT: 1,
        }       

    def __str__(self) -> str:
        value = self.value

        if value is State.PRIORITY:
            return "Véhicule prioritaire"
        if value is State.FUEL:
            return "Citerne d'essence"
        if value is State.TIRE:
            return "Increvable"
        if value is State.ACCIDENT:
            return "As du volant"

        raise ValueError(f"Carte Corrompue ! Valeur reçue : {self!r}")

    def __iter__(self):
        for s in self.get_content().keys():
            if s in self.value:
                yield s

Card = Distance | Hazard | Remedy | Safety

class CardShoe:
    __card_classes: list[type] = [Distance, Hazard, Remedy, Safety]

    def __init__(self):
        self.__content: list[Card] = sum((cls_.generate_all() for cls_ in self.__card_classes), [])
        self.__remaining_distances: int = sum(Distance.get_content().values())
        shuffle(self.__content)

    def deal(self, number=Rule.FIRST_DEAL) -> list[Card]:
        return [self.draw() for _ in range(number)]

    def has_distances(self) -> bool:
        return self.__remaining_distances > 0

    def draw(self) -> Card:
        card = self.__content.pop() if self.has_distances() else Distance(0)
        self.__remaining_distances -= type(card) is Distance
        return card
