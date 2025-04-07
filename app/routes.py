from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app
from .data_loader import process_csv

# Создаем Blueprint вместо прямого использования app
main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не найден'})

    file = request.files['file']
    result = process_csv(file, current_app.config['UPLOAD_FOLDER'])  # Используем current_app
    return jsonify(result)

@main_bp.route('/download/<filename>')
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
