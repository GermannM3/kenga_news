from aiogram import Router, types
from aiogram.filters import Command

# Создаем маршрутизатор
router = Router()

# Обработка команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Бот запущен и готов к работе.")
