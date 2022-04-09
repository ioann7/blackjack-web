import random

from flask import Blueprint
from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Game
from app.enums import GameState, CardOwner, GameResult


game = Blueprint('game', __name__, template_folder='templates')


@game.route('/')
@login_required
def index():
    return render_template('game/index.html', game=current_user.cur_game)


@game.route('/new', methods=('POST',))
@login_required
def new():
    if request.method == 'POST':
        if current_user.cur_game:
            return jsonify(success=False, error='game_already_started', message='Game already started')
        g = Game(user_id=current_user.id)
        db.session.add(g)
        db.session.commit()
        return jsonify(success=True, game_id=g.id, state=g.state.name)


@game.route('/info')
@login_required
def info():
    if request.args.get('last_game') == 'true':
        g = current_user.games.order_by(Game.created.desc()).first()
    else:
        g = current_user.cur_game

    if not g:
        return jsonify(success=False, error='game_not_found', message='Game not found. Try start new game')
    if g.state == GameState.started:
        return jsonify(g.to_dict())
    elif g.state == GameState.finished:
        return jsonify(g.to_dict(include_dealer_cards=True))


@game.route('/take_card')
@login_required
def take_card():
    g = current_user.cur_game
    if not g:
        return jsonify(success=False, error='game_not_found', message='Game not found. Try start new game')
    elif g.state == GameState.finished:
        return jsonify(success=False, error='game_already_finished', message='Game already finished')
    card = random.choice(g.deck_of_cards)
    card.owner = CardOwner.player
    player_score = sum(card.weight for card in g.player_cards)
    if player_score == 21:
        g.result = GameResult.win
    if player_score > 21:
        g.result = GameResult.lose
    db.session.commit()
    return jsonify(success=True, game_info=g.to_dict())


@game.route('/stand')
@login_required
def stand():
    g = current_user.cur_game
    if not g:
        return jsonify(success=False, error='game_not_found', message='Game not found. Try start new game')
    elif g.state == GameState.finished:
        return jsonify(success=False, error='game_already_finished', message='Game already finished')
    while True:
        dealer_score = sum(card.weight for card in g.dealer_cards)
        if dealer_score > 21:
            break
        elif dealer_score < 17:
            card = random.choice(g.deck_of_cards)
            card.owner = CardOwner.dealer
        else:
            break
    player_score = sum(card.weight for card in g.player_cards)
    dealer_score = sum(card.weight for card in g.dealer_cards)
    if player_score == 21:
        g.result = GameResult.win
    elif player_score > 21:
        g.result = GameResult.lose
    elif player_score > dealer_score:
        g.result = GameResult.win
    elif dealer_score > 21:
        g.result = GameResult.win
    elif player_score < dealer_score:
        g.result = GameResult.lose
    elif player_score == dealer_score:
        g.result = GameResult.tie
    db.session.commit()
    return jsonify(success=True, game_info=g.to_dict(include_dealer_cards=True))


@game.route('/history')
@login_required
def history():
    # FIXME сделать ограничение на количество игр, например 100
    return jsonify(success=True, games=[game.result_dict() for game in current_user.games.all()])
