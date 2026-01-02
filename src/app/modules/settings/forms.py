from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class GlobalSettingsForm(FlaskForm):
    # General Settings
    dashboard_refresh_interval = IntegerField('Dashboard refresh interval', 
                                     validators=[DataRequired(), NumberRange(min=1, max=60)], default=5)

    # Session and Security Settings
    session_timeout = IntegerField('Session timeout', 
                                   validators=[DataRequired(), NumberRange(min=1)], default=30)
    password_min_length = IntegerField('Password minimum length', 
                                       validators=[DataRequired(), NumberRange(min=6, max=50)], default=8)

    submit = SubmitField('Save')


class DockerHostForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    enabled = BooleanField('Enabled', default=True)
    submit = SubmitField('Add Host')
