import os
import dotenv


dotenv.load_dotenv('.env')


class Configuration:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blackjack.db'
    SECRET_KEY = os.environ['SECRET_KEY']
