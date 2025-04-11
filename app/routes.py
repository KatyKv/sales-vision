# Стандартные библиотеки
import os
import logging
import time
from datetime import datetime

# Сторонние библиотеки
import pandas as pd
import xlsxwriter
from flask import (
    Blueprint, render_template, request, jsonify,
    send_from_directory, current_app, session,
    redirect, url_for, flash, send_file, Response,
    stream_with_context
)
from flask_login import login_user, logout_user, current_user, login_required

# Внутренние модули
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditForm
from app.models import User
from .analytics import (
    load_data, calculate_metrics, sales_by_date,
    sales_by_month, top_products, sales_by_region,
    average_price_per_product
)
from .visualization import (
    plot_sales_trend, plot_top_products, plot_sales_by_region,
    plot_average_price_per_product, is_enough_data
)
from .data_loader import process_csv


# Создаем Blueprint вместо прямого использования app
main_bp = Blueprint("main", __name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),   # лог в файл
        logging.StreamHandler()           # лог в консоль
    ]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@main_bp.route('/upload', methods=['POST'])
def upload():
    session.pop('saved_filename', None)
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

@main_bp.route("/")
def home():
    context = {
        'for_beginning': 'Аналитика продаж для начинающих продавцов',
        'for_active': 'Аналитика продаж для действующих продавцов',
        'for_brends': 'Аналитика продаж для брендов и агенств'
    }
    return render_template("home.html", **context)


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # что делает эта команда??
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались', 'success')
        return redirect(url_for('main.login'))
    return render_template('registration.html', form=form, title='Register')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.load_csv'))  # сделать форму загрузки csv
        else:
            print('Введены неверные данные')
            return render_template('login.html', form=form, title='Login')


@main_bp.route('/edit', methods=['GET', 'POST'])
def edit():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    user = User.query.get(current_user.id)
    form = EditForm(obj=user)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # что делает эта команда??
        user.password = hashed_password
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('Вы успешно изменили данные', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit.html', form=form, title='Edit')


@main_bp.route('/logout')
def logout():
    logout_user()  # завершает сессию пользователя (удаляет логин, куки и т.п.)
    return redirect(url_for('main.home'))


@main_bp.route('/account')
@login_required  # не даёт открыть маршрут, если пользователь не залогинен
def account():
    form = LoginForm()
    return render_template('account.html', form=form, title='Account')


@main_bp.route('/load_csv', methods=['GET', 'POST'])
def load_csv():
    return render_template('load_csv.html')

# Временная функция для тестирования визуализации. Потом, наверное, не нужна
def df_to_html(df, limit=10):
    """Преобразует DataFrame в HTML-таблицу с ограничением строк"""
    return f"""
    <div class="table-responsive">
        <h4>Первые {limit} строк</h4>
        {df.head(limit).to_html(classes='table table-striped table-bordered')}
        <h4>Последние {limit} строк</h4>
        {df.tail(limit).to_html(classes='table table-striped table-bordered')}
        <p>Всего строк: {len(df)}</p>
    </div>
    """

# ТЕСТОВАЯ СТРАНИЦА ВИЗУАЛИЗАЦИИ! УДАЛИТЬ В ФИНАЛЕ.
@main_bp.route("/visualizations")
def visualizations():
    filename = session.get('saved_filename')
    if not filename:
        return "Файл не найден. Сначала загрузите CSV.", 400
    data_file_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    if not os.path.exists(data_file_path):
        return "Файл не найден на сервере", 404
    df = load_data(data_file_path)
    logging.info('Файл успешно загружен')

    metrics = calculate_metrics(df)
    for key, value in metrics.items():
        logging.info(f"{key}: {value:.2f}")

    # Подготовка данных для таблиц и графиков
    df_limit = min(10, len(df))
    df_by_date = sales_by_date(df)
    df_day_limit = min(10, len(df_by_date))
    df_by_month = sales_by_month(df)
    df_month_limit = min(10, len(df_by_month))
    df_by_region = sales_by_region(df)
    df_region_limit = min(10, len(df_by_region))
    df_top_revenue = top_products(df, by='revenue')
    df_top_quantity = top_products(df, by='quantity')
    top_number = min(10, len(df_top_revenue))
    df_avg_price = average_price_per_product(df)
    avg_price_number = min(10, len(df_avg_price))

    # Список визуализаций, где чередуются таблицы и графики
    visualizations_for_print = [
        {
            "title": "Исходные данные",
            "table": df_to_html(df, df_limit),
            "graph": None
        },
        {
            "title": "Выручка по месяцам",
            "table": df_to_html(df_by_month, df_month_limit),
            "graph": (
                plot_sales_trend(df_by_month)
                if is_enough_data(df_by_month, 'ym')
                else "<p>Недостаточно данных для графика "
                     "(нужно более 1 месяца)</p>"
            )
        },
        {
            "title": "Выручка по дням",
            "table": df_to_html(df_by_date, df_day_limit),
            "graph": (
                plot_sales_trend(df_by_date, 'day')
                if is_enough_data(df_by_date, 'date')
                else "<p>Недостаточно данных для графика "
                     "(нужно более 1 дня)</p>"
            )
        },
        {
            "title": "Топ продуктов по выручке",
            "table": df_to_html(df_top_revenue, top_number),
            "graph": plot_top_products(df_top_revenue, top=top_number)
        },
        {
            "title": "Топ продуктов по количеству",
            "table": df_to_html(df_top_quantity, top_number),
            "graph": plot_top_products(df_top_quantity, 'quantity', top_number)
        },
        {
            "title": "Выручка по регионам",
            "table": df_to_html(df_by_region, df_region_limit),
            "graph": plot_sales_by_region(df_by_region)
        },
        {
            "title": "Средняя цена по товарам",
            "table": df_to_html(df_avg_price, avg_price_number),
            "graph": plot_average_price_per_product(df_avg_price, top=avg_price_number)
        }
    ]

    return render_template(
        'visualizations.html',
        visualizations=visualizations_for_print,
        metrics=metrics
    )


@main_bp.route('/generate_report', methods=['POST'])
def generate_report():

    filename = session.get('saved_filename')
    if not filename:
        return "Файл не найден. Сначала загрузите CSV.", 400

    data_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    df = load_data(data_file_path)

    metrics = calculate_metrics(df)

    df_by_date = sales_by_date(df)
    df_by_month = sales_by_month(df)
    df_by_region = sales_by_region(df)
    df_top = top_products(df)

    graphs = {
        "Выручка по месяцам": plot_sales_trend(df_by_month),
        "Топ продуктов": plot_top_products(df_top),
        "Топ продуктов по количеству": plot_top_products(df_top),
        "Выручка по регионам": plot_sales_by_region(df_by_region)
    }
    return render_template('load_csv.html', graphs=graphs, metrics=metrics)

@main_bp.route('/progress')
def progress():
    def generate():
        for i in range(101):
            time.sleep(0.1)  # Имитация задержки обработки
            yield f"data: {i}\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@main_bp.route('/download_report')
def download_report():
    try:
        filename = request.args.get('filename')
        if not filename:
            return "Не указано имя файла", 400

        file_path = os.path.join(RESULT_FOLDER, filename)
        if not os.path.exists(file_path):
            return "Файл отчета не найден", 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Ошибка скачивания: {str(e)}", 500
