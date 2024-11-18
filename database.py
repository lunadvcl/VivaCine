import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    # Используем контекстный менеджер для работы с базой данных
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()

        # Создание таблицы с нужными полями
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE
            )
        ''')

        # Проверка, если таблица пуста, то добавляем администратора
        cursor.execute('SELECT * FROM User WHERE username = ?', ('admin',))
        admin_exists = cursor.fetchone()

        if not admin_exists:
            # Хешируем пароль администратора
            hashed_password = generate_password_hash('admin')

            # Вставляем администратора в таблицу
            cursor.execute('''
                INSERT INTO User (first_name, last_name, email, password, username)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin', 'admin1@gmail.com', hashed_password, 'admin'))

        # Коммит изменений
        db.commit()

# Инициализация базы данных и добавление администратора при первом запуске
init_db()
