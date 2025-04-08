from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
from app import routes

def create_app():

    # Загрузка конфигурации
    app.config.from_pyfile('../config.py')

    # Создание папки для загрузок
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Регистрация Blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app