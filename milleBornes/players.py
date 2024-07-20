from dataclasses import dataclass, field

from .cards import *
from .rules import BadMove, Rule, SafetyUse, CounterThrust


@dataclass
class Player:
    name: str
    score: int = 0
    count200: int = 0
    hazards: State = State.LIGHT
    safeties: State = State(0)
    hand: list[Card] = field(default_factory=list)

    def __ilshift__(self, other: Card) -> Self:
        match other:
            case Distance(d): self.run(d)
            case Hazard(s): self.take_hazard(s)
            case Remedy(s): self.take_remedy(s)
            case Safety(s): self.take_safety(s)

        return self

    def take_safety(self, state: State):
        self.hazards &= ~state
        self.safeties |= state

        raise SafetyUse("Rejouez !")

    def take_remedy(self, state: State):
        if self.hazards is State(0):
            raise BadMove("Vous n'avez rien à parer.")

        if self.hazards & state is State(0):
            raise BadMove("Votre parade ne correspond pas à l'attaque que vous subissez.")

        self.hazards &= ~state

    def take_hazard(self, hazard: State):
        if hazard & self.hazards is State.SPEED:
            raise BadMove("Votre adversaire roule déjà au ralenti.")

        if hazard in ~State.SPEED and self.hazards.ignore_speed():
            raise BadMove("Votre adversaire subit déjà les effets d'une autre attaque.")

        if hazard in self.safeties:
            raise BadMove("Cette attaque n'a plus d'effet sur votre adversaire.")

        for i, card in enumerate(self.hand):
            if type(card) is Safety and hazard in (safety := card.value):
                self.hand.pop(i)
                self.hazards &= ~safety
                self.safeties |= safety
                raise CounterThrust("Coup fourré !")
        else:
            self.hazards |= hazard

    def run(self, distance: int):
        if self.hazards.ignore_speed() != State(0):
            raise BadMove("Vous êtes sous l'effet d'un attaque et ne pouvez donc pas rouler.")
        
        if State.SPEED in self.hazards and distance > Rule.SPEED:
            raise BadMove(f"Vous ne pouvez pas dépasser les {Rule.SPEED} Bornes par tour.")

        if self.count200 >= Rule.MAX_USE_200 and distance == 200:
            raise BadMove("Vous ne pouvez plus jouer de carte 200 Bornes.")

        if self.score + distance > Rule.WINNING_DISTANCE:
            raise BadMove("Vous ne pouvez pas dépasser les 1000 Bornes !")

        self.score += distance
        self.count200 += (distance == 200)

