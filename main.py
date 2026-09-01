from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.handlers import router


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Анализатор читабельности текста"
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


app.include_router(router)