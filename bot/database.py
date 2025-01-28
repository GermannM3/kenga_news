import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS published_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована.")

def is_news_published(title):
    """Проверяет, была ли новость уже опубликована."""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM published_news WHERE title = ?', (title,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_news_to_db(title):
    """Добавляет новость в базу данных."""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO published_news (title) VALUES (?)', (title,))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(f"Новость уже существует: {title}")
    conn.close()
