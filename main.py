import app.routes


from app import app
from app.game.blueprint import game


app.register_blueprint(game, url_prefix='/game')


from app.models import db, User, Game, Card


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Game': Game, 'Card': Card}


if __name__ == '__main__':
    app.run()
