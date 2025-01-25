FROM python:3.9-slim

WORKDIR /app

# Устанавливаем зависимости системы (если нужно)
RUN apt-get update && apt-get install -y gcc

# Обновляем pip
RUN pip install --upgrade pip

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запускаем FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
