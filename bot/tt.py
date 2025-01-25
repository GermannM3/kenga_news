import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
print(f"API_TOKEN: {API_TOKEN}")  # Отладочный вывод

if not API_TOKEN:
    raise ValueError("API_TOKEN не найден в .env файле.")