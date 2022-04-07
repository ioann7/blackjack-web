from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = StringField('Login', validators=(DataRequired(),))
    password = StringField('Password', validators=(DataRequired(),))
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')
