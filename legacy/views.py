from flask import request, jsonify, current_app
from app.data_loader import process_csv


def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        result = process_csv(file, current_app.config['UPLOAD_FOLDER'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500