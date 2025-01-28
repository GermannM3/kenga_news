from aiogram import Router, types
from aiogram.filters import Command

# Создание маршрутизатора
router = Router()

# Обработка команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Бот запущен и готов к работе!")

# Обработка команды /help
@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply("Доступные команды:\n/start - Запуск бота\n/help - Справка")
