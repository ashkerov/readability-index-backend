from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.handlers import router
from data.database import engine
from data import models

# Создаем таблицы в БД при запуске
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Readability Index App")

# Указываем FastAPI, где искать статические файлы (CSS и прочее)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

@app.get("/")
def read_root():
    # Исправлен редирект с учетом префикса /api
    return RedirectResponse(url="/api/publications", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)