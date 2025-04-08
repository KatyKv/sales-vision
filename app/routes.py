import os

from flask import (
    Blueprint, render_template, request, jsonify,
    send_from_directory, current_app, session
)

from .analytics import (
    load_data, calculate_metrics, sales_by_date,
    sales_by_month, top_products, sales_by_region
)
from .data_loader import process_csv
from .visualization import (
    plot_sales_trend, plot_top_products, plot_sales_by_region,
)

# Создаем Blueprint вместо прямого использования app
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не найден'})

    file = request.files['file']
    result = process_csv(file, current_app.config['UPLOAD_FOLDER'])  # Используем current_app
    if result.get('status') == 'success':
        session['saved_filename'] = result['saved_as']
    return jsonify(result)

@main_bp.route('/download/<filename>')
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main_bp.route("/visualizations")
def visualizations():
    filename = session.get('saved_filename')
    if not filename:
        return "Файл не найден. Сначала загрузите CSV.", 400
    data_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    df = load_data(data_file_path)

    metrics = calculate_metrics(df)
    for key, value in metrics.items():
        print(f'{key}: {value:.2f}')

    df_by_date = sales_by_date(df)
    df_by_month = sales_by_month(df)
    df_by_region = sales_by_region(df)
    df_top = top_products(df)

    graphs = {
        "Выручка по месяцам": plot_sales_trend(df_by_month),
        "Топ продуктов": plot_top_products(df_top),
        "Топ продуктов по количеству": plot_top_products(df_top, 'quantity'),
        "Выручка по регионам": plot_sales_by_region(df_by_region)
    }
    return render_template('visualizations.html', graphs=graphs)
