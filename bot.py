import telebot
from news_parser import get_latest_news  # Предположим, что у вас есть модуль для парсинга новостей

# Инициализация бота
bot = telebot.TeleBot('YOUR_BOT_TOKEN')

# Функция для отправки новостей
def send_news(chat_id):
    news = get_latest_news()
    if news:
        for item in news:
            bot.send_message(chat_id, item)
    else:
        bot.send_message(chat_id, "Новых новостей нет.")

# Пример использования
send_news('CHAT_ID') 