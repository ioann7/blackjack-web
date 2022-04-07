from enum import Enum


class GameState(Enum):
    started = 1
    finished = 2


class GameResult(Enum):
    win = 1
    tie = 2
    lose = 3
    in_progress = 4


class CardOwner(Enum):
    deck = 1
    dealer = 2
    player = 3


class Suit(Enum):
    diamond = 1
    heart = 2
    club = 3
    spade = 4
