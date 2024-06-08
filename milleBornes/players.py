from milleBornes.cards import *
from dataclasses import dataclass, field

@dataclass
class Player:
    name: str
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

