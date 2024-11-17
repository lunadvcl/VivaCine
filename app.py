from flask import Flask, render_template, request, redirect, url_for, g, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import json
from datetime import datetime


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
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Проверка наличия пользователя в сессии
            return redirect(url_for('login'))  # Перенаправляем на страницу входа
        return f(*args, **kwargs)
    return decorated_function
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
@login_required
def la_casa_de_papel():
    return render_template('La Casa de Papel.html')
@app.route('/pirates')
@login_required
def pirates():
    return render_template('pirates.html')
@app.route('/leon')
@login_required
def leon():
    return render_template('leon.html')
@app.route('/russ')
@login_required
def russ():
    return render_template('russ.html')
@app.route('/fast')
@login_required
def fast():
    return render_template('fast.html')
@app.route('/ocean')
@login_required
def ocean():
    return render_template('ocean.html')
@app.route('/kevin')
@login_required
def kevin ():
    return render_template('kevin.html')
@app.route('/oppenheimer')
@login_required
def oppenheimer():
    return render_template('oppenheimer.html')
@app.route('/wolf')
@login_required
def wolf():
    return render_template('wolf.html')
@app.route('/Insidious')
@login_required
def insidious():
    return render_template('Insidious.html')
@app.route('/avatar')
@login_required
def avatar():
    return render_template('avatar.html')
@app.route('/Interstellar')
@login_required
def Interstellar():
    return render_template('Interstellar.html')
@app.route('/russ2')
@login_required
def kitchen():
    return render_template('russ2.html')
@app.route('/Twilight')
@login_required
def Twilight():
    return render_template('Twilight.html')
@app.route('/Winx')
@login_required
def Winx():
    return render_template('Winx.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        profile_picture = request.files.get('profile_picture')

        if not all([first_name, last_name, email, password]):
            flash("Все поля обязательны для заполнения.")
            return render_template('register.html')

        if profile_picture:
            filename = os.path.join('static/uploads', profile_picture.filename)
            profile_picture.save(filename)
        else:
            filename = None

        hashed_password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO User (first_name, last_name, email, password, profile_picture)
                VALUES (?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, hashed_password, filename))
            db.commit()
        except sqlite3.Error as e:
            flash("Ошибка регистрации.")
            print(e)
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка, что оба поля были заполнены
        if not email or not password:
            flash("Email и пароль обязательны.")
            return render_template('login.html'), 400

        # Подключение к базе данных
        db = get_db()
        if db is None:
            flash("Ошибка подключения к базе данных.")
            return render_template('login.html'), 500

        cursor = db.cursor()

        try:
            # Извлечение пользователя по email
            cursor.execute('SELECT * FROM User WHERE email = ?', (email,))
            user = cursor.fetchone()

            # Если пользователь найден, проверяем пароль
            if user and check_password_hash(user[3], password):  # user[3] - предполагаем, что пароль в 4-м столбце
                # Сохраняем user_id и username в сессии
                session['user_id'] = user[0]  # ID пользователя из первого столбца
                session['username'] = user[1]  # Username из второго столбца
                flash("Вы успешно вошли в систему.")
                return redirect(url_for('index'))  # Перенаправляем на страницу чата

            # Если логин или пароль неверны
            flash("Неверные учетные данные.")
            return render_template('login.html'), 400

        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса на вход:", e)
            flash("Ошибка выполнения запроса.")
            return render_template('login.html'), 500

    # Возвращаем шаблон при GET-запросе
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("Вы вышли из системы.")
    return redirect(url_for('login'))

@app.route('/index')
def home():
    return render_template('index.html')

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


CHAT_FILE = 'chat_messages.json'
# Страница для отображения сообщений

# Загрузка сообщений из JSON файла
def load_messages():
    """Загрузка сообщений из JSON файла."""
    try:
        with open('chat_messages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_messages():
    if not os.path.exists(CHAT_FILE) or os.path.getsize(CHAT_FILE) == 0:
        initial_message = {
            'sender': 'admin',
            'message': 'We will definitely contact you. What questions do you have?',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_message('admin', initial_message['message'], initial_message['timestamp'])
        return [initial_message]

    messages = []
    with open(CHAT_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                message = json.loads(line.strip())  # Пытаемся распарсить строку
                if message:  # Проверяем, что сообщение не пустое
                    messages.append(message)
            except json.JSONDecodeError:
                continue  # Пропускаем некорректные строки
    return messages


# Страница чата
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            sender = session['username']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_message(sender, message, timestamp)
        return redirect(url_for('chat'))

    messages = get_messages()
    return render_template('chat.html', messages=messages)

# Страница админского чата
@app.route('/admin_chat', methods=['GET', 'POST'])
def admin_chat():
    if 'username' not in session:
        return redirect(url_for('login'))  # Перенаправление, если пользователь не авторизован

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            sender = session['username']  # Имя отправителя из сессии
            timestamp = '2024-11-17 12:00:00'  # Пример временной метки, замените на реальную
            save_message(sender, message, timestamp)
            flash("Сообщение отправлено.")

    # Загружаем сообщения из файла и передаем их в шаблон
    messages = load_messages()
    return render_template('admin_chat.html', messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        message = request.form['message']
        if message:
            timestamp = '2024-11-17 12:00:00'  # Пример временной метки
            save_message("User", message)
        return redirect(url_for('chat'))


def save_message(sender, message, timestamp):
    message_data = {
        "sender": sender,
        "message": message,
        "timestamp": timestamp
    }

    with open(CHAT_FILE, 'a', encoding='utf-8') as file:
        # Убедитесь, что сообщение сохраняется в нормальном текстовом виде
        json.dump(message_data, file, ensure_ascii=False)
        file.write("\n")  # Добавляем новую строку после каждого сообщения

if __name__ == '__main__':
    init_db()
    app.run(host='localhost', port=5009, debug=True)

if __name__ == '__main__':
    init_db()
    app.run(host='localhost', port=5009, debug=True)
