from flask import Flask, render_template, request, redirect, url_for, g, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
DATABASE = 'db.sqlite'

# Функция для подключения к базе данных
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Закрытие подключения при завершении запроса
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Инициализация базы данных (создание таблиц)
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            password TEXT NOT NULL,
                            profile_picture TEXT
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Movie (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            genre TEXT,
                            rating REAL,
                            description TEXT
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            message TEXT NOT NULL
                          )''')
        db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Главная страница с каталогом фильмов
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Movie")
    movies = cursor.fetchall()
    return render_template('index.html', movies=movies)

@app.route('/genres')
def genres():
    return render_template('genres.html')

# Страница библиотеки
@app.route('/library')
def library():
    return render_template('library.html')

# Страница "Для меня"
@app.route('/personal')
def personal():
    return render_template('personal.html')

# Страница поиска
@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/movie/<int:movie_id>')
@login_required
def movie_details(movie_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Movie WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    if movie is None:
        return "Movie not found", 404
    return render_template('movie_details.html', movie=movie)

@app.route('/la-casa-de-papel')
def la_casa_de_papel():
    return render_template('La Casa de Papel.html')  # Страница фильма
@app.route('/pirates')
def pirates():
    return render_template('pirates.html')  # Страница фильма
@app.route('/leon')
def leon():
    return render_template('leon.html')  # Страница фильма
@app.route('/russ')
def russ():
    return render_template('russ.html')  # Страница фильма
@app.route('/fast')
def fast():
    return render_template('fast.html')  # Страница фильма
@app.route('/ocean')
def ocean():
    return render_template('ocean.html')  # Страница фильма

# Страница для отображения сообщений
@app.route('/messages')
def show_messages():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    return render_template('messages.html', messages=messages)

# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        profile_picture = request.form.get('profile_picture', None)

        # Хешируем пароль перед сохранением
        hashed_password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO User (first_name, last_name, password, profile_picture)
            VALUES (?, ?, ?, ?)
        ''', (first_name, last_name, hashed_password, profile_picture))
        db.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form['first_name']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM User WHERE first_name = ?', (first_name,))
        user = cursor.fetchone()

        # Проверяем, что пользователь существует и пароль правильный
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        return "Неверные данные"

    return render_template('login.html')

# Профиль пользователя
@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM User WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        first_initial = user[1][0].upper()  # Первая буква имени
        last_initial = user[2][0].upper()   # Первая буква фамилии
        profile_picture = user[4]            # Фото профиля

        return render_template('profile.html', user=user, first_initial=first_initial, last_initial=last_initial, profile_picture=profile_picture)
    return redirect(url_for('login'))

# Отключение от сессии (выход)
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Страница для отображения категорий
@app.route('/categories')
def categories():
    return genres()

# Страница для отображения сообщения (сохранения)
@app.route('/submit_message', methods=['POST'])
def submit_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    db.commit()

    return redirect(url_for('index'))  # Перенаправление на главную страницу

if name == '__main__':
    init_db()  # Создаем базу данных и таблицы
    app.run(host='localhost', port=5002, debug=True)
