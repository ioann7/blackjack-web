from datetime import datetime
import random

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from .enums import GameState, CardOwner, Suit, GameResult

CARDS = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
    'A': 11,
}


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True)
    password_hash = db.Column(db.String(128))
    money = db.Column(db.Integer, nullable=False)
    games = db.relationship('Game', backref='user', lazy='dynamic')

    @property
    def cur_game(self):
        """Return None if started game was not found"""
        return self.games.filter(Game.result == GameResult.in_progress).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User username={self.username}>'


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    dealers_open_card_id = db.Column(db.Integer)
    result = db.Column(db.Enum(GameResult), default=GameResult.in_progress)
    cards = db.relationship('Card', lazy='dynamic', backref='game')
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_cards()

    def result_dict(self):
        data = {
            'id': self.id,
            'state': self.state.name,
            'result': self.result.name,
            'created': str(self.created),
        }
        return data

    def to_dict(self, include_dealer_cards=False):
        data = {
            'id': self.id,
            'state': self.state.name,
            'result': self.result.name,
            'player_cards': [card.to_dict() for card in self.player_cards],
            'dealer_open_card': self.dealer_open_card.to_dict(),
            'created': str(self.created),
        }
        if include_dealer_cards:
            data['deck_of_cards'] = [card.to_dict() for card in self.deck_of_cards]
            data['dealer_cards'] = [card.to_dict() for card in self.dealer_cards]
            data['dealers_closed_cards'] = [card.to_dict() for card in self.dealers_closed_cards]
        return data

    def generate_cards(self):
        for name, weight in CARDS.items():
            for suit in Suit:
                self.cards.append(Card(name=name, weight=weight, suit=suit, owner=CardOwner.deck))
        player_and_dealer_cards = random.sample(self.cards.all(), 4)
        player_cards, dealer_cards = player_and_dealer_cards[:2], player_and_dealer_cards[2:]
        for card in player_cards:
            print('player cards', card)
            card.owner = CardOwner.player
        for card in dealer_cards:
            print('dealer cards', card)
            card.owner = CardOwner.dealer

    @property
    def state(self):
        if self.result == GameResult.in_progress:
            return GameState.started
        return GameState.finished

    @property
    def deck_of_cards(self):
        return [card for card in self.cards.all() if card.owner == CardOwner.deck]

    @property
    def player_cards(self):
        return [card for card in self.cards.all() if card.owner == CardOwner.player]

    @property
    def dealer_cards(self):
        return [card for card in self.cards.all() if card.owner == CardOwner.dealer]

    @property
    def dealer_open_card(self):
        # FIXME MAYBE THERE IS A BUG HERE. MAYBE self.dealers_cards returns in different orders. NEED TESTS
        return self.dealer_cards[0]

    @property
    def dealers_closed_cards(self):
        return [card for card in self.dealer_cards if card.id != self.dealer_cards[0].id]

    def __repr__(self):
        return f'<Game id={self.id} state={self.state} user_id={self.user_id}>'


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    suit = db.Column(db.Enum(Suit))
    game_id = db.Column(db.Integer, db.ForeignKey(Game.id))
    owner = db.Column(db.Enum(CardOwner))
    is_garbage = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'weight': self.weight,
            'suit': self.suit.name,
            'game_id': self.game_id,
            'owner': self.owner.name,
        }

    def __repr__(self):
        return f'<Card name={self.name} game_id={self.game_id} owner={self.owner}>'
