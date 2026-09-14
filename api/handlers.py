# api/handlers.py
from fastapi import APIRouter, Request, Query, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

# Импортируем нашу функцию подключения к БД и модель Publication
from data.database import get_db
from data.models import Publication

from fastapi import APIRouter, Request, Query, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text # <-- НУЖНО ДЛЯ СЫРОГО SQL

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 0. Роут для перенаправления во вкладку "Лента" без указания ID
@router.get("/publications/feed")
def publication_feed_general(db: Session = Depends(get_db)):
    # ORM: Берем первую опубликованную запись
    first_pub = db.query(Publication).filter(Publication.status == "опубликован").first()
    if first_pub:
        return RedirectResponse(url=f"/publications/{first_pub.id}", status_code=303)
    return RedirectResponse(url="/publications", status_code=303)

# 1. СТРАНИЦА: Плитка (Поиск и получение через ORM)
@router.get("/publications")
def publications_grid(
    request: Request,
    genre: str = Query("", description="Фильтрация по жанру"),
    db: Session = Depends(get_db) # Внедряем сессию БД
):
    # ORM: Получаем все услуги, кроме удаленных
    query = db.query(Publication).filter(Publication.status != "удален")

    if genre:
        # ORM: Поиск подстроки без учета регистра (ilike)
        query = query.filter(Publication.genre.ilike(f"%{genre}%"))

    filtered_pubs = query.all()

    # Пока считаем лайки из связей ORM
    for p in filtered_pubs:
        p.likes_count = len(p.likes)

    return templates.TemplateResponse(
        request=request,
        name="publications_grid.html",
        context={
            "publications": filtered_pubs,
            "current_genre": genre,
        }
    )

# 2. СТРАНИЦА: Черновик (Получение через ORM)
@router.get("/publications/draft")
def publication_draft(request: Request, db: Session = Depends(get_db)):
    # ORM: Ищем именно черновик
    draft = db.query(Publication).filter(Publication.status == "черновик").first()
    
    return templates.TemplateResponse(
        request=request,
        name="publication_draft.html",
        context={
            "publication": draft
        }
    )

@router.get("/publications/{pub_id}")
def publication_feed(
    request: Request,
    pub_id: int,
    next_pub: bool = Query(False, alias="next"),
    db: Session = Depends(get_db)
):
    pubs = db.query(Publication).filter(Publication.status != "удален").order_by(Publication.id).all()
    
    current_idx = next((i for i, p in enumerate(pubs) if p.id == pub_id), None)
    
    if current_idx is None:
        return {"error": "Публикация не найдена"}

    if next_pub:
        next_idx = current_idx + 1
        if next_idx >= len(pubs):
            pub_to_show = pubs[0]
        else:
            pub_to_show = pubs[next_idx]
    else:
        pub_to_show = pubs[current_idx]
        
    pub_to_show.likes_count = len(pub_to_show.likes)

    return templates.TemplateResponse(
        request=request,
        name="publication_feed.html",
        context={
            "publication": pub_to_show
        }
    )

    # --- POST МЕТОДЫ ДЛЯ ЛАБОРАТОРНОЙ №2 ---

# 1. POST: Создание или обновление черновика (ORM)
@router.post("/publications/draft")
def save_draft(
    title: str = Form("Новый текст"),
    genre: str = Form(""),
    avg_length: int = Form(0),
    unique_words_share: str = Form(""),
    description: str = Form(""),
    image_url: str = Form(""),
    video_url: str = Form(""),
    db: Session = Depends(get_db)
):
    # По ТЗ: у пользователя не более 1 черновика. Ищем его.
    draft = db.query(Publication).filter(Publication.status == "черновик").first()
    
    if not draft:
        # Если черновика нет, создаем новый (ORM)
        draft = Publication(
            title=title, genre=genre, avg_length=avg_length,
            unique_words_share=unique_words_share, description=description,
            image_url=image_url, video_url=video_url,
            status="черновик", creator_id=1
        )
        db.add(draft)
    else:
        # Если есть, обновляем данные (ORM)
        draft.title = title
        draft.genre = genre
        draft.avg_length = avg_length
        draft.unique_words_share = unique_words_share
        draft.description = description
        draft.image_url = image_url
        draft.video_url = video_url

    db.commit()
    return RedirectResponse(url="/publications/draft", status_code=303)

# 2. POST: Публикация карточки (ORM)
@router.post("/publications/{pub_id}/publish")
def publish_draft(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if pub and pub.status == "черновик":
        pub.status = "опубликован" # Смена статуса через ORM
        db.commit()
    # После публикации перекидываем на главную (плитку)
    return RedirectResponse(url="/publications", status_code=303)

# 3. POST: Удаление карточки (Сырой SQL, без ORM)
@router.post("/publications/{pub_id}/delete")
def delete_publication(pub_id: int, db: Session = Depends(get_db)):
    # По ТЗ: логическое удаление выполняется SQL запросом UPDATE, без ORM
    sql_query = text("UPDATE publications SET status = 'удален' WHERE id = :id")
    db.execute(sql_query, {"id": pub_id})
    db.commit()
    
    return RedirectResponse(url="/publications", status_code=303)