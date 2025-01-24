import aiohttp
from bs4 import BeautifulSoup
import re
from cachetools import cached, TTLCache
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from dotenv import load_dotenv
import os
from aiogram import Bot
import asyncio

# Загружаем переменные окружения из файла .env
load_dotenv()

logger = logging.getLogger(__name__)

# Получаем API-ключ из .env
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Кэш на 10 минут
cache = TTLCache(maxsize=100, ttl=600)

# Ключевые слова для поиска новостей
KEYWORDS = ["xbox", "AI", "КНДР", "Россия", "экономика", "космос"]

# Функция для получения новостей по ключевым словам
@cached(cache)
async def fetch_news(keyword):
    """Получает новости по ключевому слову."""
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}&language=ru&sortBy=publishedAt&pageSize=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def publish_news(bot: Bot):
    """Публикует новости в канал."""
    from bot.database import is_news_published, add_news_to_db

    try:
        for keyword in KEYWORDS:
            news_data = await fetch_news(keyword)
            articles = news_data.get("articles", [])

            for article in articles:
                title = article.get("title", "Без заголовка")
                description = article.get("description", "Без описания")
                url = article.get("url", "#")

                if not is_news_published(title):
                    # Формируем хэштеги
                    hashtags = " ".join([f"#{keyword}" for keyword in KEYWORDS])

                    # Формируем сообщение с хэштегами и подписью
                    message = (
                        f"**{title}**\n\n"
                        f"{description}\n\n"
                        f"[Читать далее]({url})\n\n"
                        f"{hashtags}\n\n"
                        "🦘 Подписаться: @keng_news"
                    )

                    # Отправка сообщения с задержкой
                    await bot.send_message(
                        chat_id=os.getenv("PUBLICATION_CHANNEL_ID"),
                        text=message
                    )
                    add_news_to_db(title)
                    logger.info(f"Новость опубликована: {title}")

                    # Задержка 2 секунды между сообщениями
                    await asyncio.sleep(2)

                else:
                    logger.info(f"Новость уже опубликована: {title}")

    except Exception as e:
        logger.error(f"Ошибка при публикации новостей: {e}")
