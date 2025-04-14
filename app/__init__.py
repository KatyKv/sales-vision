from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    # Загрузка конфигурации
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # Создание папки для загрузок
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Регистрация Blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Глобальные обработчики ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app