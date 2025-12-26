# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
#                          ^^^^^^^^^^^^^^ ADD THIS
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
#                                             ^^^^^^  ^^^^^^^ ADD THESE
from models import User

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters")
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])  # Now works!
    submit = SubmitField('Login')

class SelectCategoryForm(FlaskForm):
    category = SelectField(
        'Select Category',
        choices=[
            ('Python', 'Python'),
            ('JavaScript', 'JavaScript'),
            ('SQL', 'SQL'),
            ('Git', 'Git'),
            ('CSS and HTML', 'CSS and HTML')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Start Exam')

def generate_exam_form(questions):
    class ExamForm(FlaskForm):
        submit = SubmitField('Submit Answers')

    for q in questions:
        for idx, option in enumerate(q['options']):
            field_name = f"q{q['id']}_opt{idx}"
            setattr(ExamForm, field_name, BooleanField(option))

    return ExamForm()