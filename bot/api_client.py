import aiohttp
import logging
import os

logger = logging.getLogger(__name__)

async def fetch_news(keyword):
    """Получает новости по ключевому слову"""
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={os.getenv('NEWS_API_KEY')}&language=ru&sortBy=publishedAt&pageSize=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            logger.error(f"Ошибка при запросе к API: {response.status}")
            return {"articles": []} 