from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    show_password = BooleanField('Show password')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    show_password = BooleanField('Show passwords')
    submit = SubmitField('Register')

    def validate_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')

class AccountForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired(), Email()])    
    oldPassword = StringField('Old Password', render_kw={'readonly': True}, id="oldPassword")
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long')])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    showPassword = BooleanField('Show passwords', id='showPassword')

    update = SubmitField('Update')
    logout = SubmitField('Logout')
    delete = SubmitField('Delete Account')

    def populate(self, user):
        if user is not None:
            self.username.data = user['username']
            self.email.data = user['email']
            self.oldPassword.data = user['password']