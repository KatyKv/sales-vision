from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app import db, bcrypt
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        email = db.session.query(User).filter_by(email=email.data).first()
        if email:
            raise ValidationError('Такой email уже существует в базе данных')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомни меня')
    submit = SubmitField('Войти')

    def validate_email(self, email):
        user = db.session.query(User).filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Такой email не зарегистрирован в базе данных')

    def validate_password(self, password):
        user = db.session.query(User).filter_by(email=self.email.data).first()  # Находим пользователя по email
        if user is None or not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError('Неправильный пароль')


class EditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Подтвердить')