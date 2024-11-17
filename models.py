from app import db  # Импортируйте объект db из вашего приложения

class BrowsingHistory(db.Model):
    __tablename__ = 'browsing_history'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор записи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ID пользователя
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)  # ID фильма
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())  # Время добавления записи

    # Связи (необязательно, но удобно для использования)
    user = db.relationship('User', backref='history')  # Связь с таблицей пользователей
    movie = db.relationship('Movie', backref='watched_by')  # Связь с таблицей фильмов
