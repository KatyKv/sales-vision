from flask import render_template, request, jsonify, send_from_directory
from .data_loader import process_csv
from . import app  # Импорт созданного в __init__.py приложения


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не найден'})

    file = request.files['file']
    result = process_csv(file, app.config['UPLOAD_FOLDER'])
    return jsonify(result)


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)