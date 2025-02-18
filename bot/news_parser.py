import logging

logger = logging.getLogger(__name__)

async def get_latest_news():
    try:
        from bot.utils import fetch_news  # Ленивый импорт
        news = []
        for keyword in ["AI", "Россия", "экономика"]:  # Пример ключевых слов
            data = await fetch_news(keyword)
            news.extend(data.get("articles", []))
        logger.info(f"Получено новостей: {len(news)}")
        return news
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        return [] 