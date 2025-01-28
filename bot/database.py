import redis
import logging
import os

logger = logging.getLogger(__name__)

def init_redis():
    """Инициализация подключения к Redis"""
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        username=os.getenv("REDIS_USER"),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=os.getenv("REDIS_SSL", "true").lower() == "true",
        ssl_cert_reqs=None,
        decode_responses=True
    )

def is_news_published(redis_client, title):
    """Проверяет, была ли новость уже опубликована"""
    return redis_client.sismember("published_news", title)

def add_news_to_db(redis_client, title):
    """Добавляет новость в Redis"""
    try:
        redis_client.sadd("published_news", title)
        logger.info(f"Новость добавлена в Redis: {title}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении в Redis: {str(e)}")
