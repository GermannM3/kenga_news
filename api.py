from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiogram import Bot
import os

app = FastAPI()

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

# Создаем объект бота
bot = Bot(token=os.getenv("API_TOKEN"))

# Модель для запроса
class MessageRequest(BaseModel):
    chat_id: str
    message: str

@app.post("/send_message")
async def send_message(request: MessageRequest):
    try:
        await bot.send_message(
            chat_id=request.chat_id,
            text=request.message,
            parse_mode="HTML"
        )
        return {"status": "success", "message": "Message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)