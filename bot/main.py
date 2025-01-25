import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.database import init_db
from bot.handlers import router
from bot.utils import publish_news
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен и другие переменные из .env
API_TOKEN = os.getenv("API_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
PUBLICATION_CHANNEL_ID = os.getenv("PUBLICATION_CHANNEL_ID")

# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация маршрутизатора
dp.include_router(router)

# Основная функция
async def main():
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from bot.database import init_db
    from bot.utils import publish_news

    init_db()
    bot = Bot(token=os.getenv("API_TOKEN"))
    await publish_news(bot)  # Запускаем публикацию новостей

# Для запуска из командной строки
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}")
