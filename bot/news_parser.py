import logging
from bot.utils import fetch_news  # Импорт функции для получения новостей

logger = logging.getLogger(__name__)

def get_latest_news():
    try:
        # Пример получения новостей
        news = []
        for keyword in ["AI", "Россия", "экономика"]:  # Пример ключевых слов
            data = await fetch_news(keyword)
            news.extend(data.get("articles", []))
        logger.info(f"Получено новостей: {len(news)}")
        return news
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        return [] 