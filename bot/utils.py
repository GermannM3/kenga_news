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

# Загружаем переменные окружения из файла .env
load_dotenv()

logger = logging.getLogger(__name__)

# Получаем API-ключ из .env
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Кэш на 10 минут
cache = TTLCache(maxsize=100, ttl=600)

# Ключевые слова для поиска новостей
KEYWORDS = ["xbox", "AI", "КНДР", "Россия", "экономика", "космос"]

def clean_text(text):
    """Очищает текст от символов, которые могут нарушить HTML-разметку."""
    if not text:
        return ""
    return re.sub(r"[\*_\[\]()]", "", text)

@cached(cache)
async def fetch_news(keyword):
    """Получает новости по ключевому слову."""
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}&language=ru&sortBy=publishedAt&pageSize=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(12),
    retry=retry_if_exception_type(TelegramRetryAfter)
)
async def send_news_with_retry(bot: Bot, chat_id: str, message: str, image_url: str = None):
    """Отправляет новость с повторными попытками при ошибке 429."""
    try:
        if image_url:
            await bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=message,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML"
            )
    except TelegramRetryAfter as e:
        logger.warning(f"Превышен лимит отправки. Повтор через {e.retry_after} сек.")
        await asyncio.sleep(e.retry_after + 2)
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке: {e}")
        raise

async def publish_news(bot: Bot):
    """Публикует новости в канал с регулировкой скорости."""
    from bot.database import is_news_published, add_news_to_db

    try:
        for keyword in KEYWORDS:
            news_data = await fetch_news(keyword)
            articles = news_data.get("articles", [])

            for article in articles:
                title = clean_text(article.get("title", "Без заголовка"))
                description = clean_text(article.get("description", "Без описания"))
                url = article.get("url", "#")
                image_url = article.get("urlToImage", "")

                if not is_news_published(title):
                    relevant_hashtags = [
                        f"#{k}" for k in KEYWORDS
                        if k.lower() in title.lower() or k.lower() in description.lower()
                    ]
                    hashtags = " ".join(relevant_hashtags) if relevant_hashtags else ""

                    message = (
                        f"<b>{title}</b>\n\n"
                        f"{description}\n\n"
                        f"<a href='{url}'>Читать далее</a>\n\n"
                        f"{hashtags}\n\n"
                        "🦘 Подписаться: @keng_news"
                    )

                    await send_news_with_retry(
                        bot=bot,
                        chat_id=os.getenv("PUBLICATION_CHANNEL_ID"),
                        message=message,
                        image_url=image_url
                    )

                    add_news_to_db(title)
                    logger.info(f"Новость опубликована: {title}")

                    # Базовая задержка между сообщениями
                    await asyncio.sleep(12)

                else:
                    logger.info(f"Новость уже опубликована: {title}")

    except Exception as e:
        logger.error(f"Критическая ошибка при публикации новостей: {e}")
    finally:
        # Закрываем HTTP-сессии
        await bot.session.close()
