import aiohttp
from bs4 import BeautifulSoup
import re
from cachetools import cached, TTLCache
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from dotenv import load_dotenv
import os

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

# Остальные функции остаются без изменений
