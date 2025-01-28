import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.database import init_db
from bot.handlers import router
from bot.utils import publish_news
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
API_TOKEN = os.getenv("API_TOKEN")
PUBLICATION_CHANNEL_ID = os.getenv("PUBLICATION_CHANNEL_ID")

# Проверка обязательных переменных
if not API_TOKEN or not PUBLICATION_CHANNEL_ID:
    raise ValueError("Отсутствуют обязательные переменные окружения: API_TOKEN или PUBLICATION_CHANNEL_ID")

# Создание объектов бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация маршрутизатора
dp.include_router(router)

# Основная функция
async def main():
    init_db()  # Инициализация базы данных
    asyncio.create_task(publish_news(bot))  # Запуск задачи публикации новостей
    await dp.start_polling(bot, skip_updates=True)  # Пропуск старых сообщений

# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

