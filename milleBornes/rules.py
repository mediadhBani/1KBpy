from enum import IntEnum


class Rule(IntEnum):
    FIRST_DEAL = 6
    MAX_USE_200 = 2
    SPEED = 50
    WINNING_DISTANCE = 1000

class BadMove(ValueError):
    pass

class BadParse(ValueError):
    pass

class SafetyEvent(Exception):
    pass

class SafetyUse(SafetyEvent):
    pass

class CounterThrust(SafetyEvent):
    pass

