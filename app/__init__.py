from flask import Flask

def create_app():
    app = Flask(__name__)

    # Здесь позже подключим другие модули (роуты, БД, конфиг и т.д.)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
