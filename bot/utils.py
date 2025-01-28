import aiohttp
import re
import logging
import os
from aiogram import Bot
import asyncio
from bot.database import is_news_published, add_news_to_db

logger = logging.getLogger(__name__)

# API-ключ и другие настройки
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
KEYWORDS = ["xbox", "AI", "КНДР", "Россия", "экономика", "космос"]
HASHTAGS = {kw.lower(): f"#{kw.lower()}" for kw in KEYWORDS}

def clean_text(text):
    """Очищает текст от нежелательных символов"""
    return re.sub(r"[\*_\[\]()]", "", text) if text else ""

async def fetch_news(keyword):
    """Получает новости по ключевому слову"""
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}&language=ru&sortBy=publishedAt&pageSize=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()  # Исправлено здесь
            logger.error(f"Ошибка при запросе к API: {response.status}")
            return {"articles": []}

async def publish_news(bot: Bot, redis_client):
    """Публикует новости с использованием Redis"""
    try:
        while True:
            for keyword in KEYWORDS:
                news_data = await fetch_news(keyword)
                articles = news_data.get("articles", [])

                for article in articles:
                    title = clean_text(article.get("title", "Без заголовка"))
                    description = clean_text(article.get("description", "Без описания"))
                    url = article.get("url", "#")
                    image_url = article.get("urlToImage", "")

                    if is_news_published(redis_client, title):
                        logger.info(f"Новость уже опубликована: {title}")
                        continue

                    relevant_hashtags = [
                        HASHTAGS[key] for key in HASHTAGS
                        if key in title.lower() or key in description.lower()
                    ]
                    hashtags = " ".join(relevant_hashtags) if relevant_hashtags else ""

                    message = (
                        f"<b>{title}</b>\n\n{description}\n\n<a href='{url}'>Читать далее</a>\n\n"
                        f"{hashtags}\n\n🦘 Подписаться: @kenga_news"
                    )

                    try:
                        if image_url:
                            await bot.send_photo(
                                chat_id=os.getenv("PUBLICATION_CHANNEL_ID"),
                                photo=image_url,
                                caption=message,
                                parse_mode="HTML"
                            )
                        else:
                            await bot.send_message(
                                chat_id=os.getenv("PUBLICATION_CHANNEL_ID"),
                                text=message,
                                parse_mode="HTML"
                            )
                        add_news_to_db(redis_client, title)
                        logger.info(f"Новость опубликована: {title}")
                    except Exception as e:
                        logger.error(f"Ошибка при публикации: {e}")

                    await asyncio.sleep(30)
            await asyncio.sleep(3600)  # Проверка новых новостей каждый час
    except Exception as e:
        logger.error(f"Ошибка публикации: {e}")
