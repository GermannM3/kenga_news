import aiohttp
from bs4 import BeautifulSoup
import re
from cachetools import cached, TTLCache
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import logging
from dotenv import load_dotenv
import os
from aiogram import Bot
import asyncio
from aiogram.exceptions import TelegramRetryAfter

load_dotenv()
logger = logging.getLogger(__name__)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
cache = TTLCache(maxsize=100, ttl=600)
KEYWORDS = ["xbox", "AI", "КНДР", "Россия", "экономика", "космос"]

def clean_text(text):
    return re.sub(r"[\*_\[\]()]", "", text) if text else ""

@cached(cache)
async def fetch_news(keyword):
    """Запрос к NewsAPI с закрытием сессии"""
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}&language=ru&sortBy=publishedAt&pageSize=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(20),
    retry=retry_if_exception_type(TelegramRetryAfter)
)
async def send_news_with_retry(bot: Bot, chat_id: str, message: str, image_url: str = None):
    """Отправка с увеличенными задержками"""
    try:
        if image_url:
            await bot.send_photo(chat_id, image_url, caption=message, parse_mode="HTML")
        else:
            await bot.send_message(chat_id, message, parse_mode="HTML")
    except TelegramRetryAfter as e:
        wait_time = e.retry_after + 5  # +5 сек. для надежности
        logger.warning(f"Лимит! Повтор через {wait_time} сек.")
        await asyncio.sleep(wait_time)
        raise
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        raise
    finally:
        await bot.session.close()  # Закрываем сессию бота

async def publish_news(bot: Bot):
    """Публикация с улучшенным управлением ресурсами"""
    from bot.database import is_news_published, add_news_to_db

    try:
        for keyword in KEYWORDS:
            news_data = await fetch_news(keyword)
            articles = news_data.get("articles", [])

            for article in articles:
                title = clean_text(article.get("title", ""))
                if not title or is_news_published(title):
                    continue

                # Формирование сообщения
                message = (
                    f"<b>{title}</b>\n\n"
                    f"{clean_text(article.get('description', ''))}\n\n"
                    f"<a href='{article['url']}'>Читать далее</a>\n\n"
                    f"{' '.join(f'#{k}' for k in KEYWORDS if k.lower() in title.lower())}\n\n"
                    "🦘 Подписаться: @keng_news"
                )

                # Отправка с задержкой
                await send_news_with_retry(
                    bot=bot,
                    chat_id=os.getenv("PUBLICATION_CHANNEL_ID"),
                    message=message,
                    image_url=article.get("urlToImage")
                )

                add_news_to_db(title)
                logger.info(f"Опубликовано: {title}")
                await asyncio.sleep(25)  # Увеличенная базовая задержка

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        if not bot.session.closed:
            await bot.session.close()
