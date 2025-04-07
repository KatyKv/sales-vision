from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    # Загрузка конфигурации
    app.config.from_pyfile('../config.py')

    # Создание папки для загрузок
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Регистрация Blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app