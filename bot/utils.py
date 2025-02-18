import aiohttp
import re
import logging
import os
from aiogram import Bot
import asyncio
from bot.database import is_news_published, add_news_to_db
from bot.api_client import fetch_news  # Новый импорт
from bot.news_parser import get_latest_news  # Добавлен импорт

logger = logging.getLogger(__name__)

# API-ключ и другие настройки
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
KEYWORDS = ["xbox", "AI", "КНДР", "Россия", "экономика", "космос"]
HASHTAGS = {kw.lower(): f"#{kw.lower()}" for kw in KEYWORDS}

def clean_text(text):
    """Очищает текст от нежелательных символов"""
    return re.sub(r"[\*_\[\]()]", "", text) if text else ""

async def publish_news(bot, redis_client):
    try:
        # Получение новостей
        news = await get_latest_news()
        if news:
            for item in news:
                if not is_news_published(redis_client, item['id']):
                    await bot.send_message(chat_id=os.getenv("PUBLICATION_CHANNEL_ID"), text=item['text'])
                    add_news_to_db(redis_client, item['id'])
                    logger.info(f"Новость опубликована: {item['id']}")
                else:
                    logger.info(f"Новость уже опубликована: {item['id']}")
        else:
            logger.info("Новых новостей нет.")
    except Exception as e:
        logger.error(f"Ошибка при публикации новостей: {e}")
