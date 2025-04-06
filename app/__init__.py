from flask import Flask, render_template

from app.extensions import db, bcrypt, login_manager

from flask import redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import RegistrationForm, LoginForm, EditForm
from app.models import User


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
from app import routes


def create_app():


    # Здесь позже подключим другие модули (роуты, БД, конфиг и т.д.)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app


@app.route("/")
def home():
    context = {
        'for_beginning': 'Аналитика продаж для начинающих продавцов',
        'for_active': 'Аналитика продаж для действующих продавцов',
        'for_brends': 'Аналитика продаж для брендов и агенств'
    }
    return render_template("home.html", **context)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # что делает эта команда??
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('load_csv'))  #  сделать форму загрузки csv
        else:
            print('Введены неверные данные')
    return render_template('login.html', form=form, title='Login')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
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


@app.route('/logout')
def logout():
    logout_user()  # что делает эта команда??
    return redirect(url_for('home'))

@app.route('/account')
@login_required  # для чего это здесь нужно???
def account():
    return render_template('account.html')


@app.route('/load_csv', methods=['GET', 'POST'])
def load_csv():
        return render_template('load_csv.html')


