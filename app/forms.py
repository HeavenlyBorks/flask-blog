from sqlite3 import IntegrityError
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import Post, User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirmation = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is taken. Please choose a different one.")
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email is taken. Please choose a different one.")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")

class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")

    def validate_username(self, username):
        usernamedata = username.data
        user = User.query.filter_by(username=username.data).first()
        if user and usernamedata != current_user.username:
            raise ValidationError("That username is taken. Please choose a different one.")
    
    def validate_email(self, email):
        emaildata = email.data
        email = User.query.filter_by(email=email.data).first()
        if email and emaildata != current_user.email:
            raise ValidationError("That email is taken. Please choose a different one.")

class MakePost(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=100)])
    date_posted = DateField("Date Posted", validators=[Optional()], format="%m/%d/%Y")
    content = TextAreaField("Content", validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField("Make Post")

    def validate_title(self, title):
        title = Post.query.filter_by(title=title.data).first()
        if title:
            raise ValidationError("That title has already been used. Please use another one.")