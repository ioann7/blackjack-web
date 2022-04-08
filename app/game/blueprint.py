import random

from flask import Blueprint
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models import Game, User
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
        game = Game(user_id=current_user.id)
        db.session.add(game)
        db.session.commit()
        return jsonify(success=True, game_id=game.id, state=game.state.name)


@game.route('/info')
@login_required
def info():
    if request.args.get('last_game') == 'true':
        game = current_user.games.order_by(Game.created.desc()).first()
    else:
        game = current_user.cur_game

    if not game:
        return jsonify(success=False, error='game_not_found', message='Game not found. Try start new game')
    if game.state == GameState.started:
        return jsonify(game.to_dict())
    elif game.state == GameState.finished:
        return jsonify(game.to_dict(include_dealer_cards=True))


# @game.route('/info/<int:id_>', methods=('GET',))
# @login_required
# def info(id_):
#     game = Game.query.filter(Game.id == id_, Game.user_id == current_user.id).first()
#     if not game:
#         return jsonify(success=False, error='game_not_found', message='Game id not found')
#     if game.state == GameState.finished:
#         return jsonify(game.to_dict(include_dealer_cards=True))
#     else:
#         return jsonify(game.to_dict())


@game.route('/take_card')
@login_required
def take_card():
    game = current_user.cur_game
    if not game:
        return jsonify(success=False, error='game_not_found', message='Game not found. Try start new game')
    elif game.state == GameState.finished:
        return jsonify(success=False, error='game_already_finished', message='Game already finished')
    card = random.choice(game.deck_of_cards)
    card.owner = CardOwner.player
    player_score = sum(card.weight for card in game.player_cards)
    if player_score == 21:
        game.result = GameResult.win
    if player_score > 21:
        game.result = GameResult.lose
    db.session.commit()
    return jsonify(success=True, game_info=game.to_dict())


@game.route('/stand')
@login_required
def stand():
    game = current_user.cur_game
    if not game:
        return jsonify(success=False, error='game_not_found', message='Game not found. Try start new game')
    elif game.state == GameState.finished:
        return jsonify(success=False, error='game_already_finished', message='Game already finished')
    while True:
        dealer_score = sum(card.weight for card in game.dealer_cards)
        if dealer_score > 21:
            break
        elif dealer_score < 17:
            card = random.choice(game.deck_of_cards)
            card.owner = CardOwner.dealer
        else:
            break
    player_score = sum(card.weight for card in game.player_cards)
    dealer_score = sum(card.weight for card in game.dealer_cards)
    if player_score == 21:
        game.result = GameResult.win
    elif player_score > 21:
        game.result = GameResult.lose
    elif player_score > dealer_score:
        game.result = GameResult.win
    elif dealer_score > 21:
        game.result = GameResult.win
    elif player_score < dealer_score:
        game.result = GameResult.lose
    elif player_score == dealer_score:
        game.result = GameResult.tie
    db.session.commit()
    return jsonify(success=True, game_info=game.to_dict(include_dealer_cards=True))


@game.route('/history')
@login_required
def history():
    return jsonify(success=True, games=[game.result_dict() for game in current_user.games.all()])
