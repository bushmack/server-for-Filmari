import sqlite3
import os

DB_PATH = "collections.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            film_id INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_film_to_collection(user_id: str, film_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO collections (user_id, film_id) VALUES (?, ?)", (user_id, film_id))
    conn.commit()
    conn.close()

def get_user_collections(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT film_id FROM collections WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]