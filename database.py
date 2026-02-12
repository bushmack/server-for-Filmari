import sqlite3
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Используем постоянное место для базы данных
DB_PATH = "/app/data/film_app.db"

def init_db():
    logger.info("Инициализация базы данных")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_collections (
                user_id TEXT,
                film_id INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pair_sessions (
                session_id TEXT PRIMARY KEY,
                user_a TEXT,
                user_b TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_genres (
                session_id TEXT,
                user_id TEXT,
                genre TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_votes (
                session_id TEXT,
                user_id TEXT,
                film_id INTEGER,
                vote BOOLEAN
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_shown_films (
                session_id TEXT,
                film_id INTEGER
            )
        """)
        conn.commit()
        logger.info("База данных инициализирована")

def add_film_to_collection(user_id: str, film_id: int):
    logger.info(f"Добавление фильма {film_id} пользователю {user_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_collections (user_id, film_id) VALUES (?, ?)", (user_id, film_id))
        conn.commit()
        logger.info(f"Фильм {film_id} успешно добавлен пользователю {user_id}")

def get_user_collections(user_id: str) -> list:
    logger.info(f"Получение подборки пользователя {user_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT film_id FROM user_collections WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        result = [row[0] for row in rows]
        logger.info(f"Найдено {len(result)} фильмов в подборке пользователя {user_id}")
        return result

def create_pair_session(session_id: str, user_a: str, user_b: str):
    logger.info(f"Создание сессии {session_id} между {user_a} и {user_b}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pair_sessions (session_id, user_a, user_b) VALUES (?, ?, ?)",
                       (session_id, user_a, user_b))
        conn.commit()
        logger.info(f"Сессия {session_id} создана")

def save_genres_for_user_in_session(session_id: str, user_id: str, genres: list):
    logger.info(f"Сохранение жанров {genres} для пользователя {user_id} в сессии {session_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM session_genres WHERE session_id = ? AND user_id = ?", (session_id, user_id))
        for genre in genres:
            cursor.execute("INSERT INTO session_genres (session_id, user_id, genre) VALUES (?, ?, ?)",
                           (session_id, user_id, genre))
        conn.commit()
        logger.info(f"Жанры сохранены для пользователя {user_id} в сессии {session_id}")

def get_genres_for_users_in_session(session_id: str):
    logger.info(f"Получение жанров для сессии {session_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, genre FROM session_genres WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        user_genres = {}
        for user_id, genre in rows:
            if user_id not in user_genres:
                user_genres[user_id] = []
            user_genres[user_id].append(genre)
        logger.info(f"Жанры для сессии {session_id}: {user_genres}")
        return user_genres

def save_vote_in_session(session_id: str, user_id: str, film_id: int, vote: bool):
    logger.info(f"Сохранение голоса пользователя {user_id} за фильм {film_id} в сессии {session_id}: {vote}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO session_votes (session_id, user_id, film_id, vote) VALUES (?, ?, ?, ?)",
                       (session_id, user_id, film_id, vote))
        conn.commit()
        logger.info(f"Голос сохранён")

def get_votes_in_session(session_id: str):
    logger.info(f"Получение голосов для сессии {session_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, film_id, vote FROM session_votes WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        votes = {}
        for user_id, film_id, vote in rows:
            if user_id not in votes:
                votes[user_id] = {}
            votes[user_id][film_id] = vote
        logger.info(f"Голоса для сессии {session_id}: {votes}")
        return votes

def get_users_in_session(session_id: str):
    logger.info(f"Получение пользователей для сессии {session_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_a, user_b FROM pair_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            logger.info(f"Пользователи в сессии {session_id}: {row[0]}, {row[1]}")
            return row[0], row[1]
        logger.info(f"Сессия {session_id} не найдена")
        return None, None

def add_shown_film_to_session(session_id: str, film_id: int):
    logger.info(f"Добавление показанного фильма {film_id} в сессии {session_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO session_shown_films (session_id, film_id) VALUES (?, ?)",
                       (session_id, film_id))
        conn.commit()
        logger.info(f"Фильм {film_id} добавлен в показанные для сессии {session_id}")

def get_shown_films_in_session(session_id: str):
    logger.info(f"Получение показанных фильмов для сессии {session_id}")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT film_id FROM session_shown_films WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        result = [row[0] for row in rows]
        logger.info(f"Показанные фильмы в сессии {session_id}: {result}")
        return result