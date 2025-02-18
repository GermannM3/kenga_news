import logging

logger = logging.getLogger(__name__)

def get_latest_news():
    try:
        # Пример получения новостей (замените на ваш код)
        news = fetch_news_from_api()
        logger.info(f"Получено новостей: {len(news)}")
        return news
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        return [] 