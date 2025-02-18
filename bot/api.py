from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
import logging
import redis
from bot.database import init_redis, is_news_published, add_news_to_db
from bot.utils import publish_news
from bot.handlers import router
import requests

app = FastAPI()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

logger = logging.getLogger(__name__)

class MessageRequest(BaseModel):
    chat_id: str
    message: str

class TelegramAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, json=payload)
        return response.json()

@app.on_event("startup")
async def startup_event():
    # Инициализация Redis
    redis_client = init_redis()
    try:
        redis_client.ping()
        logger.info("✅ Redis подключен!")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Redis: {str(e)}")
        raise
    
    # Тестовое сообщение
    await bot.send_message(chat_id=os.getenv("PUBLICATION_CHANNEL_ID"), text="Тестовое сообщение")
    
    # Запуск бота и задачи публикации новостей
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    asyncio.create_task(publish_news(bot, redis_client))

@app.post("/send_message")
async def send_message(request: MessageRequest):
    try:
        await bot.send_message(chat_id=request.chat_id, text=request.message, parse_mode="HTML")
        return {"status": "success", "message": "Message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
