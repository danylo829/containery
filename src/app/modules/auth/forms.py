from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminSetupForm(FlaskForm):
    def __init__(self, min_length=8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password.validators.append(
            Length(min=min_length, max=50)
        )

    username = StringField('Username', validators=[DataRequired(), Length(max=150)])
    name = StringField('Full Name (optional)', validators=[Length(max=150)])
    email = StringField('Email (optional)', validators=[Length(max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Create Admin User')