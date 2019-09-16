from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, BooleanField
from wtforms.validators import EqualTo, Email, Length, ValidationError

from models import User

'''
[VARIABLE] = [FieldType]('[LABEL]', [
        validators.[VALIDATOR TYPE](message=('[VALIDATOR ERROR'))
    ])
'''

password_length: int = 8


class SignUp(FlaskForm):
    username: StringField = StringField('Username', [
        validators.DataRequired(message='Don\'t be shy!'),
        Length(min=6)
    ])
    email: StringField = StringField('Email', [
        Length(min=6, message=u'Little short for an email address?'),
        Email(message='That\'s not a valid email address.'),
        validators.DataRequired(message='That\'s not a valid email address.')
    ])

    password_hash: StringField = PasswordField('Password', validators=[
        validators.DataRequired(message="Please enter a password."),
        Length(min=password_length, message="Too Short"),
    ])
    confirm_password_hash: StringField = PasswordField('Confirm Password',
                                                       validators=[validators.DataRequired(),
                                                                   EqualTo('password_hash'),
                                                                   Length(min=password_length)])

    def validate_email(self, email: str):
        """Email validation.
        """
        user: str = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_username(self, username: str):
        """username validation."""
        user: str = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    submit = SubmitField(u'Sign Up')


class SignIn(FlaskForm):
    email = StringField('Email', [
        validators.DataRequired(message='That\'s not a valid email address.')
    ])

    password_hash = PasswordField('Password', validators=[
        validators.DataRequired(message="Wrong password."),
    ])

    remember = BooleanField('remember me')

    submit = SubmitField(u'Sign In')
