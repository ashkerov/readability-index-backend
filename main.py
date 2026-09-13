from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles # 1. Импортируем StaticFiles
import uvicorn

from api.handlers import router

app = FastAPI(title="Readability Index App")

# 2. Указываем FastAPI, где искать статические файлы (наш CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

@app.get("/")
def read_root():
    return RedirectResponse(url="/publications", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)