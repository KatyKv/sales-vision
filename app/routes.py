from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app, send_file, session
from .data_loader import process_csv
from flask import redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import RegistrationForm, LoginForm, EditForm
from app import db, bcrypt
from app.models import User
import os
#from .analytics import generate_analysis
from .visualization import plot_sales_trend, plot_top_products, plot_sales_by_region
import pandas as pd
import xlsxwriter
import logging


######
from .analytics import load_data, calculate_metrics, sales_by_date, sales_by_month, top_products, sales_by_region

######

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

#############################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
###############################

@main_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не найден'})

    file = request.files['file']
    result = process_csv(file, current_app.config['UPLOAD_FOLDER'])  # Используем current_app

    if result.get('status') == 'success':
        session['saved_filename'] = result['saved_as']
    return jsonify(result)



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
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, title='Edit')


@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main_bp.route('/account')
@login_required
def account():
    return render_template('account.html', username=current_user.username)


@main_bp.route('/load_csv', methods=['GET', 'POST'])
def load_csv():
    return render_template('load_csv.html')

#############################
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
        "Топ продуктов по количеству": plot_top_products(df_top, 'quantity'),
        "Выручка по регионам": plot_sales_by_region(df_by_region)
    }
    return render_template('load_csv.html', graphs=graphs, metrics=metrics)

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

