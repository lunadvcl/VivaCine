from flask import Flask,jsonify,send_from_directory, render_template, request, redirect, url_for, g, session, flash
import sqlite3
import os
from functools import wraps
import json
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
DATABASE = 'db.sqlite'
UPLOAD_FOLDER = 'static/profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.after_request
def add_ngrok_skip_header(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

def get_db():
    """
    Функция для получения соединения с базой данных SQLite.
    Она создаёт соединение, если его ещё нет, и обрабатывает ошибки.
    """
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

def init_db():
    with app.app_context():
        db = get_db()
        if db is None:
            print("Database connection failed during initialization.")
            return
        cursor = db.cursor()
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                first_name TEXT NOT NULL,
                                last_name TEXT NOT NULL,
                                email TEXT NOT NULL UNIQUE,
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
            cursor.execute('''CREATE TABLE IF NOT EXISTS Messages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                email TEXT NOT NULL,
                                message TEXT NOT NULL
                              )''')
            db.commit()
        except sqlite3.Error as e:
            print("Database initialization error:", e)


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
@app.route('/action')
def action():
    return render_template('action.html')
@app.route('/comedy')
def comedy():
    return render_template('comedy.html')
@app.route('/drama')
def drama():
    return render_template('drama.html')

# Страница библиотеки
@app.route('/library')
def library():
    return render_template('library.html')
# Путь к папке с изображениями
POSTERS_FOLDER = "posters"

# Пример данных о постерах
posters = [
    {"id": 1, "filename": "poster1.jpg", "title": "Movie Poster 1"},
    {"id": 2, "filename": "poster2.jpg", "title": "Movie Poster 2"},
    {"id": 3, "filename": "poster3.jpg", "title": "Movie Poster 3"},
    {"id": 4, "filename": "poster4.jpg", "title": "Movie Poster 4"},
    {"id": 5, "filename": "poster5.jpg", "title": "Movie Poster 5"},
    {"id": 6, "filename": "poster6.jpg", "title": "Movie Poster 6"},
    {"id": 7, "filename": "poster7.jpg", "title": "Movie Poster 7"},
    {"id": 8, "filename": "poster8.jpg", "title": "Movie Poster 8"},
    {"id": 9, "filename": "poster9.jpg", "title": "Movie Poster 9"},
]

@app.route('/api/posters', methods=['GET'])
def get_posters():
    """
    Возвращает список постеров в формате JSON.
    """
    return jsonify(posters)

@app.route('/posters/<filename>', methods=['GET'])
def download_poster(filename):
    """
    Позволяет скачивать постер из папки POSTERS_FOLDER.
    """
    try:
        return send_from_directory(POSTERS_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404



# Страница поиска
@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/movie/<int:movie_id>')
@login_required
def movie_details(movie_id):
    """
    Отображает информацию о фильме и добавляет его в историю просмотров.
    """
    db = get_db()
    cursor = db.cursor()

    # Получаем данные о фильме из таблицы Movie
    cursor.execute("SELECT * FROM Movie WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    if movie:
        movie_info = {
            'id': movie[0],
            'title': movie[1],
            'genre': movie[2],
            'rating': movie[3],
            'description': movie[4]
        }
        return render_template('movie_details.html', movie=movie_info)
    else:
        return "Movie not found", 404

    if movie is None:
        return "Movie not found", 404

    # Добавляем запись в таблицу BrowsingHistory
    watched_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO BrowsingHistory (user_id, movie_title, watched_at)
        VALUES (?, ?, ?)
    ''', (1, movie['title'], watched_at))  # Здесь user_id = 1 для примера
    db.commit()

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
@app.route('/Animated')
@login_required
def Animated():
    return render_template('Animated.html')

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
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    flash("Logged out successfully.")
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT first_name, last_name, username, email, birth_date, registered_at, profile_picture FROM User WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()

    if user:
        user_info = {

        'first_name': user[0],
        'last_name': user[1],
        'username': user[2],
        'email': user[3],
        'birth_date': user[4],
        'registered_at': user[5],
        'profile_picture': user[6] if user[6] else 'default.jpg'

        }
        return render_template('profile.html', user=user_info)
    else:
        return "Пользователь не найден", 404


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/browsing_history')
def browsing_history():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем его на страницу входа

    # Получаем историю просмотра текущего пользователя
    db = get_db()
    cursor = db.cursor()

    # Извлекаем все записи из таблицы BrowsingHistory для текущего пользователя
    cursor.execute('''
        SELECT movie_title, watched_at FROM BrowsingHistory WHERE user_id = ?
        ORDER BY watched_at DESC
    ''', (user_id,))
    movies = cursor.fetchall()

    return render_template('history.html', movies=movies)


def create_tables():
    """
    Создаёт таблицу BrowsingHistory, если её нет.
    """
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BrowsingHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_title TEXT NOT NULL,
                watched_at TEXT NOT NULL
            )
        ''')
        db.commit()

# Вызов функции создания таблиц при запуске приложения
create_tables()


# Проверяем, существует ли папка, и если нет — создаём её
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if 'user_id' not in session:  # Проверка, авторизован ли пользователь
        return redirect(url_for('login'))

    user_id = session['user_id']  # Получение текущего пользователя
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':

        # Получение данных из формы
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form['username']
        email = request.form['email']
        birth_date = request.form['birth_date']

        profile_picture = request.files.get('profile_picture')
        profile_picture_name = None

        if profile_picture:
            profile_picture_name = f"{user_id}_{profile_picture.filename}"
            profile_picture.save(os.path.join(app.static_folder, 'profile_pictures', profile_picture_name))

        # Обновление данных в базе данных
        cursor.execute("""
                    UPDATE User
                    SET first_name = ?, last_name = ?, username = ?, email = ?, birth_date = ?, profile_picture = ?
                    WHERE id = ?
                """, (first_name, last_name, username, email, birth_date, profile_picture_name, user_id))
        db.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))


    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    return render_template('edit_profile.html', user=user)


def add_user(first_name, last_name, username, email, birth_date=None, profile_picture=None):
    conn = sqlite3.connect('database.db')
    with conn:
        conn.execute("""
            INSERT INTO User (first_name, last_name, username, email, birth_date, profile_picture)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (first_name, last_name, username, email, birth_date, profile_picture))
    print("Пользователь добавлен!")

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    with conn:
        user = conn.execute("SELECT * FROM User WHERE id = ?;", (user_id,)).fetchone()
    return user

def update_user(user_id, first_name=None, last_name=None, username=None, email=None, birth_date=None, profile_picture=None):
    conn = sqlite3.connect('database.db')
    with conn:
        conn.execute("""
            UPDATE User
            SET first_name = COALESCE(?, first_name),
                last_name = COALESCE(?, last_name),
                username = COALESCE(?, username),
                email = COALESCE(?, email),
                birth_date = COALESCE(?, birth_date),
                profile_picture = COALESCE(?, profile_picture)
            WHERE id = ?;
        """, (first_name, last_name, username, email, birth_date, profile_picture, user_id))
    print("Профиль пользователя обновлен!")

def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    with conn:
        conn.execute("DELETE FROM User WHERE id = ?;", (user_id,))
    print("Пользователь удален!")


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
    db.commit()

    session.clear()  # Clear the session data
    flash('Ваш аккаунт был удалён.', 'info')
    return redirect(url_for('login'))



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


@app.route('/leave_review', methods=['GET', 'POST'])
def leave_review():
    if request.method == 'POST':
        content = request.form['content']
        rating = request.form['rating']

        if not content or not rating:
            flash('Пожалуйста, заполните все поля!')
            return redirect(url_for('leave_review'))

        user_id = 1  # Здесь добавь реальную логику для получения ID текущего пользователя
        movie_id = 1  # Здесь добавь реальный ID фильма

        # Добавление отзыва
        with sqlite3.connect('db.sqlite') as conn:
            conn.execute('''
                INSERT INTO review (content, rating, user_id, movie_id)
                VALUES (?, ?, ?, ?)
            ''', (content, rating, user_id, movie_id))
            conn.commit()

        flash('Отзыв успешно добавлен!')
        return redirect(url_for('leave_review'))

    return render_template('leave_review.html')


if __name__ == '__main__':
    init_db()
    create_tables()
    app.run(host='localhost', port=5003, debug=True)


