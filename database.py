"""
Модуль для работы с базой данных SQLite.
Содержит функции для инициализации БД и работы с таблицами.
"""

import sqlite3
import os
import logging
from typing import List, Tuple, Optional, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Определение пути к файлу базы данных
# Для локальной разработки используем папку data в текущей директории
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "film_app.db")

# Создаем директорию для БД, если её нет
os.makedirs(DB_DIR, exist_ok=True)

logger.info(f"База данных будет сохранена по пути: {DB_PATH}")


def init_db() -> bool:
    """
    Инициализирует базу данных и создает все необходимые таблицы.

    Returns:
        bool: True если инициализация прошла успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info("=" * 50)
    logger.info("НАЧАЛО ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ")
    logger.info("=" * 50)

    create_tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS user_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            film_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, film_id)
        )
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_user_collections_user_id 
        ON user_collections(user_id)
        """,

        """
        CREATE TABLE IF NOT EXISTS pair_sessions (
            session_id TEXT PRIMARY KEY,
            user_a TEXT NOT NULL,
            user_b TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_pair_sessions_users 
        ON pair_sessions(user_a, user_b)
        """,

        """
        CREATE TABLE IF NOT EXISTS session_genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            genre TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES pair_sessions(session_id) ON DELETE CASCADE,
            UNIQUE(session_id, user_id, genre)
        )
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_session_genres_session 
        ON session_genres(session_id)
        """,

        """
        CREATE TABLE IF NOT EXISTS session_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            film_id INTEGER NOT NULL,
            vote BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES pair_sessions(session_id) ON DELETE CASCADE,
            UNIQUE(session_id, user_id, film_id)
        )
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_session_votes_session 
        ON session_votes(session_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_session_votes_film 
        ON session_votes(film_id)
        """,

        """
        CREATE TABLE IF NOT EXISTS session_shown_films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            film_id INTEGER NOT NULL,
            shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES pair_sessions(session_id) ON DELETE CASCADE,
            UNIQUE(session_id, film_id)
        )
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_session_shown_films_session 
        ON session_shown_films(session_id)
        """
    ]

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Выполняем все SQL запросы для создания таблиц
            for sql in create_tables_sql:
                cursor.execute(sql)

            conn.commit()

            # Проверяем, что таблицы создались
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"Созданы таблицы: {[table[0] for table in tables]}")

            logger.info("=" * 50)
            logger.info("БАЗА ДАННЫХ УСПЕШНО ИНИЦИАЛИЗИРОВАНА")
            logger.info("=" * 50)

            return True

    except sqlite3.Error as e:
        logger.error(f"ОШИБКА при инициализации базы данных: {e}")
        logger.error("=" * 50)
        raise


def add_film_to_collection(user_id: str, film_id: int) -> bool:
    """
    Добавляет фильм в коллекцию пользователя.

    Args:
        user_id: ID пользователя
        film_id: ID фильма

    Returns:
        bool: True если добавление успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Добавление фильма {film_id} в коллекцию пользователя {user_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO user_collections (user_id, film_id)
                VALUES (?, ?)
            """, (user_id, film_id))

            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"✅ Фильм {film_id} успешно добавлен пользователю {user_id}")
                return True
            else:
                logger.info(f"ℹ️ Фильм {film_id} уже был в коллекции пользователя {user_id}")
                return False

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при добавлении фильма: {e}")
        raise


def get_user_collections(user_id: str) -> List[int]:
    """
    Получает список ID фильмов в коллекции пользователя.

    Args:
        user_id: ID пользователя

    Returns:
        List[int]: Список ID фильмов

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Получение коллекции пользователя {user_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT film_id 
                FROM user_collections 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))

            rows = cursor.fetchall()
            result = [row[0] for row in rows]

            logger.info(f"Найдено {len(result)} фильмов в коллекции пользователя {user_id}")
            return result

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении коллекции: {e}")
        raise


def create_pair_session(session_id: str, user_a: str, user_b: str) -> bool:
    """
    Создает новую парную сессию.

    Args:
        session_id: Уникальный ID сессии
        user_a: ID первого пользователя
        user_b: ID второго пользователя

    Returns:
        bool: True если создание успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Создание сессии {session_id} между {user_a} и {user_b}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO pair_sessions (session_id, user_a, user_b)
                VALUES (?, ?, ?)
            """, (session_id, user_a, user_b))

            conn.commit()

            logger.info(f"✅ Сессия {session_id} успешно создана")
            return True

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при создании сессии: {e}")
        raise


def save_genres_for_user_in_session(session_id: str, user_id: str, genres: List[str]) -> bool:
    """
    Сохраняет выбранные жанры пользователя в сессии.

    Args:
        session_id: ID сессии
        user_id: ID пользователя
        genres: Список жанров

    Returns:
        bool: True если сохранение успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Сохранение жанров для пользователя {user_id} в сессии {session_id}: {genres}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Удаляем старые жанры пользователя в этой сессии
            cursor.execute("""
                DELETE FROM session_genres 
                WHERE session_id = ? AND user_id = ?
            """, (session_id, user_id))

            # Добавляем новые жанры
            for genre in genres:
                cursor.execute("""
                    INSERT OR IGNORE INTO session_genres (session_id, user_id, genre)
                    VALUES (?, ?, ?)
                """, (session_id, user_id, genre))

            conn.commit()

            logger.info(f"✅ Жанры сохранены для пользователя {user_id} в сессии {session_id}")
            return True

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при сохранении жанров: {e}")
        raise


def get_genres_for_users_in_session(session_id: str) -> Dict[str, List[str]]:
    """
    Получает словарь жанров для всех пользователей в сессии.

    Args:
        session_id: ID сессии

    Returns:
        Dict[str, List[str]]: Словарь {user_id: [список жанров]}

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Получение жанров для сессии {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_id, genre 
                FROM session_genres 
                WHERE session_id = ?
                ORDER BY user_id, genre
            """, (session_id,))

            rows = cursor.fetchall()

            result: Dict[str, List[str]] = {}
            for user_id, genre in rows:
                if user_id not in result:
                    result[user_id] = []
                result[user_id].append(genre)

            logger.info(f"Найдены жанры для {len(result)} пользователей в сессии {session_id}")
            return result

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении жанров: {e}")
        raise


def save_vote_in_session(session_id: str, user_id: str, film_id: int, vote: bool) -> bool:
    """
    Сохраняет голос пользователя за фильм в сессии.

    Args:
        session_id: ID сессии
        user_id: ID пользователя
        film_id: ID фильма
        vote: Голос (True - like, False - dislike)

    Returns:
        bool: True если сохранение успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Сохранение голоса пользователя {user_id} за фильм {film_id} в сессии {session_id}: {vote}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO session_votes (session_id, user_id, film_id, vote)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, film_id, vote))

            conn.commit()

            logger.info(f"✅ Голос успешно сохранен")
            return True

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при сохранении голоса: {e}")
        raise


def get_votes_in_session(session_id: str) -> Dict[str, Dict[int, bool]]:
    """
    Получает все голоса в сессии.

    Args:
        session_id: ID сессии

    Returns:
        Dict[str, Dict[int, bool]]: Словарь {user_id: {film_id: vote}}

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Получение голосов для сессии {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_id, film_id, vote 
                FROM session_votes 
                WHERE session_id = ?
                ORDER BY user_id, film_id
            """, (session_id,))

            rows = cursor.fetchall()

            result: Dict[str, Dict[int, bool]] = {}
            for user_id, film_id, vote in rows:
                if user_id not in result:
                    result[user_id] = {}
                result[user_id][film_id] = bool(vote)

            logger.info(f"Найдены голоса от {len(result)} пользователей в сессии {session_id}")
            return result

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении голосов: {e}")
        raise


def get_users_in_session(session_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Получает пользователей в сессии.

    Args:
        session_id: ID сессии

    Returns:
        Tuple[Optional[str], Optional[str]]: (user_a, user_b) или (None, None) если сессия не найдена

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Получение пользователей для сессии {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_a, user_b 
                FROM pair_sessions 
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"В сессии {session_id}: user_a={row[0]}, user_b={row[1]}")
                return row[0], row[1]

            logger.info(f"Сессия {session_id} не найдена")
            return None, None

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении пользователей сессии: {e}")
        raise


def add_shown_film_to_session(session_id: str, film_id: int) -> bool:
    """
    Добавляет фильм в список показанных в сессии.

    Args:
        session_id: ID сессии
        film_id: ID фильма

    Returns:
        bool: True если добавление успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Добавление показанного фильма {film_id} в сессию {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO session_shown_films (session_id, film_id)
                VALUES (?, ?)
            """, (session_id, film_id))

            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"✅ Фильм {film_id} добавлен в показанные для сессии {session_id}")
                return True
            else:
                logger.info(f"ℹ️ Фильм {film_id} уже был показан в сессии {session_id}")
                return False

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при добавлении показанного фильма: {e}")
        raise


def get_shown_films_in_session(session_id: str) -> List[int]:
    """
    Получает список показанных фильмов в сессии.

    Args:
        session_id: ID сессии

    Returns:
        List[int]: Список ID фильмов

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Получение показанных фильмов для сессии {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT film_id 
                FROM session_shown_films 
                WHERE session_id = ?
                ORDER BY shown_at DESC
            """, (session_id,))

            rows = cursor.fetchall()
            result = [row[0] for row in rows]

            logger.info(f"Найдено {len(result)} показанных фильмов в сессии {session_id}")
            return result

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении показанных фильмов: {e}")
        raise


def delete_session(session_id: str) -> bool:
    """
    Удаляет сессию и все связанные с ней данные.

    Args:
        session_id: ID сессии

    Returns:
        bool: True если удаление успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Удаление сессии {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Из-за ON DELETE CASCADE, связанные записи удалятся автоматически
            cursor.execute("""
                DELETE FROM pair_sessions 
                WHERE session_id = ?
            """, (session_id,))

            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"✅ Сессия {session_id} успешно удалена")
                return True
            else:
                logger.info(f"ℹ️ Сессия {session_id} не найдена")
                return False

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при удалении сессии: {e}")
        raise


def get_session_status(session_id: str) -> Optional[str]:
    """
    Получает статус сессии.

    Args:
        session_id: ID сессии

    Returns:
        Optional[str]: Статус сессии или None если сессия не найдена

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Получение статуса сессии {session_id}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT status 
                FROM pair_sessions 
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Статус сессии {session_id}: {row[0]}")
                return row[0]

            logger.info(f"Сессия {session_id} не найдена")
            return None

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении статуса сессии: {e}")
        raise


def update_session_status(session_id: str, status: str) -> bool:
    """
    Обновляет статус сессии.

    Args:
        session_id: ID сессии
        status: Новый статус

    Returns:
        bool: True если обновление успешно

    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    logger.info(f"Обновление статуса сессии {session_id} на '{status}'")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE pair_sessions 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (status, session_id))

            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"✅ Статус сессии {session_id} обновлен на '{status}'")
                return True
            else:
                logger.info(f"ℹ️ Сессия {session_id} не найдена")
                return False

    except sqlite3.Error as e:
        logger.error(f"❌ Ошибка при обновлении статуса сессии: {e}")
        raise


# Если файл запускается напрямую, выполняем инициализацию
if __name__ == "__main__":
    print("=" * 60)
    print("ЗАПУСК ПРЯМОЙ ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ")
    print("=" * 60)

    try:
        init_db()
        print("\n✅ База данных успешно инициализирована!")
        print(f"📁 Файл БД: {DB_PATH}")
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации: {e}")

    print("=" * 60)