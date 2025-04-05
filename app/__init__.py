from flask import Flask
import os

app = Flask(__name__)

# Загрузка конфигурации
app.config.from_pyfile('../config.py')

# Создание папки для загрузок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Импорт маршрутов в самом конце
from . import routes