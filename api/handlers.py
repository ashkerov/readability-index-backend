# api/handlers.py
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates

from data.collections import publications

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 1. СТРАНИЦА: Плитка карточек (Список всех услуг)
# api/handlers.py

@router.get("/publications")
def publications_grid(
    request: Request,
    genre: str = Query("", description="Фильтрация по жанру") 
):
    filtered_pubs = [p for p in publications if p["status"] != "удален"]

    if genre:
        # Теперь поиск динамичный: ищет совпадение части слова без учета регистра
        filtered_pubs = [
            p for p in filtered_pubs 
            if genre.lower() in p["genre"].lower()
        ]

    for p in filtered_pubs:
        p["likes_count"] = len(p["likes"])

    return templates.TemplateResponse(
        request=request,
        name="publications_grid.html",
        context={
            "publications": filtered_pubs,
            "current_genre": genre,
        }
    )

# 2. СТРАНИЦА: Добавление (Черновик)
# Важно: этот роут должен быть выше /publications/{pub_id}, чтобы слово 'draft' не воспринялось как ID
@router.get("/publications/draft")
def publication_draft(request: Request):
    # По ТЗ: отображается именно та услуга, которая в статусе 'черновик'
    draft = next((p for p in publications if p["status"] == "черновик"), None)
    
    return templates.TemplateResponse(
        request=request,
        name="publication_draft.html",
        context={
            "publication": draft
        }
    )

# Специальный роут для вкладки "Лента" (без указания ID)
@router.get("/publications/feed")
def publication_feed_general():
    from fastapi.responses import RedirectResponse
    # Ищем первую опубликованную запись
    first_pub = next((p for p in publications if p["status"] == "опубликован"), None)
    if first_pub:
        return RedirectResponse(url=f"/publications/{first_pub['id']}", status_code=303)
    return RedirectResponse(url="/publications", status_code=303)

# 3. СТРАНИЦА: Лента (Формат TikTok по ID)
# api/handlers.py

@router.get("/publications/{pub_id}")
def publication_feed(
    request: Request,
    pub_id: int,
    next_pub: bool = Query(False, alias="next")
):
    current_idx = next((i for i, p in enumerate(publications) if p["id"] == pub_id), None)
    
    if current_idx is None:
        return {"error": "Публикация не найдена"}

    if next_pub:
        next_idx = current_idx + 1
        # Ищем следующую НЕ удаленную карточку
        while next_idx < len(publications):
            if publications[next_idx]["status"] != "удален":
                break
            next_idx += 1
        
        # Если дошли до конца списка, зацикливаем на самую первую доступную
        if next_idx >= len(publications):
            pub_to_show = next((p for p in publications if p["status"] != "удален"), publications[0])
        else:
            pub_to_show = publications[next_idx]
    else:
        pub_to_show = publications[current_idx]
        
    pub_to_show["likes_count"] = len(pub_to_show["likes"])

    return templates.TemplateResponse(
        request=request,
        name="publication_feed.html",
        context={
            "publication": pub_to_show
        }
    )