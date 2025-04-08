from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app
from .data_loader import process_csv
from flask import redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import RegistrationForm, LoginForm, EditForm
from app import db, bcrypt
from app.models import User


# Создаем Blueprint вместо прямого использования app
main_bp = Blueprint("main", __name__)

# @main_bp.route('/')
# def index():
#     return render_template('index.html')

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
    logout_user()  # что делает эта команда??
    return redirect(url_for('main.home'))

@main_bp.route('/account')
@login_required  # для чего это здесь нужно???
def account():
    form = LoginForm()
    return render_template('account.html', form=form, title='Account')


@main_bp.route('/load_csv', methods=['GET', 'POST'])
def load_csv():
        return render_template('load_csv.html')