import os
import logging

from flask import (
    Blueprint, render_template, request, jsonify,
    send_from_directory, current_app, session,
    redirect, url_for, flash
)

from flask_login import login_user, logout_user, current_user, login_required
from app.forms import RegistrationForm, LoginForm, EditForm
from app import db, bcrypt
from app.models import User

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),   # лог в файл
        logging.StreamHandler()           # лог в консоль
    ]
)

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
            return redirect(url_for('main.load_csv'))  #  сделать форму загрузки csv
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

@main_bp.route("/visualizations")
def visualizations():
    filename = session.get('saved_filename')
    if not filename:
        return "Файл не найден. Сначала загрузите CSV.", 400
    data_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(data_file_path):
        return "Файл не найден на сервере", 404
    df = load_data(data_file_path)

    metrics = calculate_metrics(df)
    logging.info('Файл успешно загружен')
    for key, value in metrics.items():
        logging.info(f"{key}: {value:.2f}")

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
