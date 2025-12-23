# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User, db

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SelectCategoryForm(FlaskForm):
    category = SelectField('Select Category', choices=[
        ('Python', 'Python'),
        ('JavaScript', 'JavaScript'),
        ('SQL', 'SQL'),
        ('Git', 'Git'),
        ('CSS and HTML', 'CSS and HTML')
    ], validators=[DataRequired()])
    submit = SubmitField('Start Exam')

# ExamForm will be dynamically created in routes