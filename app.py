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
    if '_database' not in g:
        try:
            g._database = sqlite3.connect(DATABASE)
        except sqlite3.Error as e:
            print("Ошибка подключения к базе данных:", e)
            return None
    return g._database

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
        if db is None:
            print("Не удалось подключиться к базе данных при инициализации.")
            return
        cursor = db.cursor()
        try:
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
        except sqlite3.Error as e:
            print("Ошибка инициализации базы данных:", e)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    db = get_db()
    if db is None:
        return "Ошибка подключения к базе данных", 500
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Movie")
        movies = cursor.fetchall()
    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса к базе данных:", e)
        return "Ошибка выполнения запроса", 500
    return render_template('index.html', movies=movies)


@app.route('/categories')
def categories():
    return render_template('categories.html')

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
    return render_template('La Casa de Papel.html')
@app.route('/pirates')
def pirates():
    return render_template('pirates.html')
@app.route('/leon')
def leon():
    return render_template('leon.html')
@app.route('/russ')
def russ():
    return render_template('russ.html')
@app.route('/fast')
def fast():
    return render_template('fast.html')
@app.route('/ocean')
def ocean():
    return render_template('ocean.html')
@app.route('/kevin')
def kevin ():
    return render_template('kevin.html')
@app.route('/oppenheimer')
def oppenheimer():
    return render_template('oppenheimer.html')
@app.route('/wolf')
def wolf():
    return render_template('wolf.html')
@app.route('/Insidious')
def insidious():
    return render_template('Insidious.html')

# Страница для отображения сообщений
@app.route('/messages')
def show_messages():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    return render_template('messages.html', messages=messages)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка обязательных полей
        if not first_name or not last_name or not email or not password:
            return "Все поля обязательны для заполнения", 400

        hashed_password = generate_password_hash(password)

        # Подключение к базе данных
        db = get_db()
        if db is None:
            return "Ошибка подключения к базе данных", 500
        cursor = db.cursor()

        try:
            # Проверка, существует ли уже такой email
            cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
            if cursor.fetchone():
                return "Пользователь с таким email уже существует", 400

            # Вставка нового пользователя
            cursor.execute('''
                 INSERT INTO User (first_name, last_name, email, password)
                 VALUES (?, ?, ?, ?)
             ''', (first_name, last_name, email, hashed_password))
            db.commit()

        except sqlite3.Error as e:
            print("Ошибка при регистрации пользователя:", e)
            return "Ошибка регистрации", 500

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка обязательных полей
        if not email or not password:
            return "Email и пароль обязательны", 400

        # Подключение к базе данных
        db = get_db()
        if db is None:
            return "Ошибка подключения к базе данных", 500
        cursor = db.cursor()

        try:
            # Получение пользователя по email
            cursor.execute('SELECT * FROM User WHERE email = ?', (email,))
            user = cursor.fetchone()

        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса на вход:", e)
            return "Ошибка выполнения запроса", 500

        # Проверка пароля
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]  # Сохраняем user_id в сессии
            return redirect(url_for('index'))

        return "Неверные учетные данные", 400

    return render_template('login.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT first_name, last_name, email FROM User WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    if user:
        user_info = {
            'first_name': user[0],
            'last_name': user[1],
            'email': user[2]
        }
        return render_template('profile.html', user=user_info)
    else:
        return "Пользователь не найден", 404


@app.route('/logout')
def logout():
    session.clear()  # Очищаем данные сессии
    return redirect(url_for('login'))


# Страница для отображения сообщения (сохранения)
@app.route('/submit_message', methods=['POST'])
def submit_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return "Все поля обязательны", 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    db.commit()

    return redirect(url_for('index'))

@app.route('/show_user_columns')
def show_user_columns():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(User)")
    columns = cursor.fetchall()
    return str(columns)

@app.route('/show_users')
def show_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, first_name, last_name, password FROM User")
    users = cursor.fetchall()
    return str(users)


if name == '__main__':
    init_db()
    app.run(host='localhost', port=5009, debug=True)
