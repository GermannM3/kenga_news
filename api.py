from fastapi import FastAPI
import os

app = FastAPI()

# Добавьте проверку работоспособности
@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Берём порт из переменной окружения
    uvicorn.run("api:app", host="0.0.0.0", port=port)
