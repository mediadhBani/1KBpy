from milleBornes.cards import *
from dataclasses import dataclass, field

class Status(IntEnum):
    OK = 0
    SAFETY = 1
    COUNTER_TRHUST = 2


@dataclass
class Player:
    name: str
    score: int = 0
    count200: int = 0
    hazards: State = State.LIGHT
    safeties: State = State(0)
    status: Status = Status.OK
    hand: list[Card] = field(default_factory=list)

    def __ilshift__(self, other: Card) -> Self:
        match other:
            case Distance(d): self.run(d)
            case Hazard(s): self.take_hazard(s)
            case Remedy(s): self.take_remedy(s)
            case Safety(s): self.take_safety(s)

        return self

    def take_safety(self, state: State):
        self.status = Status.SAFETY
        self.hazards &= ~state
        self.safeties |= state

    def take_remedy(self, state: State):
        if self.hazards is State(0):
            raise ValueError(f"Vous n'avez rien à parer.")

        if self.hazards & state is State(0):
            raise ValueError(f"Vous ne pouvez pas parer avec une carte {Remedy(state)}.")

        self.hazards &= ~state

    def take_hazard(self, hazard: State):
        if hazard is State.SPEED and hazard in self.hazards:
            raise ValueError("Votre adversaire est déjà ralenti.")

        if hazard in (self.hazards & ~State.SPEED):
            raise ValueError("Votre adversaire est déjà immobilisé.")

        if hazard in self.safeties:
            raise ValueError(f"Votre adversaire est immunisé contre {Hazard(hazard)}.")

        for i, card in enumerate(self.hand):
            if type(card) is Safety and hazard in (safety := card.value):
                self.status = Status.COUNTER_TRHUST
                self.hand.pop(i)
                self.hazards &= ~safety
                self.safeties |= safety
                break
            else:
                self.hazards |= hazard

    def run(self, distance: int):
        if (state := self.hazards.ignore_speed()) != State(0):
            raise ValueError(f"Trouvez d'abord une solution à votre {Hazard(state)} !")
        
        if State.SPEED in self.hazards and distance > Rule.SPEED:
            raise ValueError(f"Vous ne pouvez pas dépasser les {Rule.SPEED} Bornes par tour.")

        if self.count200 >= Rule.MAX_USE_200 and distance == 200:
            raise ValueError(f"Vous ne pouvez plus jouer de carte 200 Bornes.")

        if self.score + distance > Rule.WINNING_DISTANCE:
            raise ValueError(f"Vous ne pouvez pas dépasser les 1000 Bornes !")

        self.score += distance
        self.count200 += (distance == 200)

