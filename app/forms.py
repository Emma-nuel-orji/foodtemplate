from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exist please choose a different one!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exist please choose a different one!')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username already exist please choose a different one!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email already exist please choose a different one!')


class FoodForm(FlaskForm):
    name = StringField('Input Your Name', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Your Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    food_name = StringField('food name', validators=[DataRequired()])
    food_quantity = StringField('food quantity', validators=[DataRequired()])
    submit = SubmitField('Order Now')


class TableForm(FlaskForm):
    day = StringField('Day', validators=[DataRequired()])
    hour = StringField('hour', validators=[DataRequired()])
    name = StringField('Full_Name', validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone Number', validators=[DataRequired()])
    person = StringField('number_persons', validators=[DataRequired()])
    submit = SubmitField('Book Now')


class BlogForm(FlaskForm):
    image = FileField('Update picture', validators=[FileAllowed(['jpg', 'png'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class MenuForm(FlaskForm):
    name = StringField('The Name Of Food', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class WeeklyForm(FlaskForm):
    subtitle = StringField('Category', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    image = FileField('Update picture', validators=[FileAllowed(['jpg', 'png'])])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
