from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from dotenv import load_dotenv
import logging
from bot.database import init_db
from bot.utils import publish_news
from bot.handlers import router

load_dotenv()

app = FastAPI()
bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

logger = logging.getLogger(__name__)

class MessageRequest(BaseModel):
    chat_id: str
    message: str

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    asyncio.create_task(publish_news(bot))

@app.post("/send_message")
async def send_message(request: MessageRequest):
    try:
        await bot.send_message(chat_id=request.chat_id, text=request.message, parse_mode="HTML")
        return {"status": "success", "message": "Message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
