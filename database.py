import sqlite3
from contextlib import contextmanager

# Используем постоянное место для базы данных
DB_PATH = "/app/data/film_app.db"

def init_db():
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

@contextmanager
def get_db_cursor():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()

def add_film_to_collection(user_id: str, film_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("INSERT INTO user_collections (user_id, film_id) VALUES (?, ?)", (user_id, film_id))

def get_user_collections(user_id: str) -> list:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT film_id FROM user_collections WHERE user_id = ?", (user_id,))
        return [row[0] for row in cursor.fetchall()]

def create_pair_session(session_id: str, user_a: str, user_b: str):
    with get_db_cursor() as cursor:
        cursor.execute("INSERT INTO pair_sessions (session_id, user_a, user_b) VALUES (?, ?, ?)",
                       (session_id, user_a, user_b))

def save_genres_for_user_in_session(session_id: str, user_id: str, genres: list):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM session_genres WHERE session_id = ? AND user_id = ?", (session_id, user_id))
        for genre in genres:
            cursor.execute("INSERT INTO session_genres (session_id, user_id, genre) VALUES (?, ?, ?)",
                           (session_id, user_id, genre))

def get_genres_for_users_in_session(session_id: str):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT user_id, genre FROM session_genres WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        user_genres = {}
        for user_id, genre in rows:
            if user_id not in user_genres:
                user_genres[user_id] = []
            user_genres[user_id].append(genre)
        return user_genres

def save_vote_in_session(session_id: str, user_id: str, film_id: int, vote: bool):
    with get_db_cursor() as cursor:
        cursor.execute("INSERT OR REPLACE INTO session_votes (session_id, user_id, film_id, vote) VALUES (?, ?, ?, ?)",
                       (session_id, user_id, film_id, vote))

def get_votes_in_session(session_id: str):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT user_id, film_id, vote FROM session_votes WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        votes = {}
        for user_id, film_id, vote in rows:
            if user_id not in votes:
                votes[user_id] = {}
            votes[user_id][film_id] = vote
        return votes

def get_users_in_session(session_id: str):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT user_a, user_b FROM pair_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
        return None, None

def add_shown_film_to_session(session_id: str, film_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("INSERT INTO session_shown_films (session_id, film_id) VALUES (?, ?)",
                       (session_id, film_id))

def get_shown_films_in_session(session_id: str):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT film_id FROM session_shown_films WHERE session_id = ?", (session_id,))
        return [row[0] for row in cursor.fetchall()]