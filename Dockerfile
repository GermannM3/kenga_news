FROM python:3.9-slim

WORKDIR /app

# Обновляем pip перед установкой зависимостей
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем и FastAPI, и бота через один процесс
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port 8000 & python -m bot.main"]
