from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from minio import Minio
import uuid
from datetime import datetime

from data.database import get_db
from data.models import Publication, User, Request, RequestItem

# Все маршруты начинаются с /api по ТЗ 3 лабы
router = APIRouter(prefix="/api")

# Подключение к локальному MinIO
minio_client = Minio(
    "localhost:9002",
    access_key="admin",
    secret_key="password123",
    secure=False
)
BUCKET_NAME = "readability"

# Функция-синглтон для получения текущего пользователя
def get_current_user_id():
    return 1

# ==========================================
# ДОМЕН: УСЛУГИ (ПУБЛИКАЦИИ/ТЕКСТЫ)
# ==========================================

# 1. GET: Получить список всех текстов с фильтрацией
@router.get("/publications")
def get_publications(max_length: int = None, genre: str = None, db: Session = Depends(get_db)):
    query = db.query(Publication).filter(Publication.status != "удален")
    
    if max_length:
        query = query.filter(Publication.avg_length <= max_length)
    if genre:
        query = query.filter(Publication.genre == genre)
        
    return query.all()

# 2. GET: Получить один текст по ID
@router.get("/publications/{pub_id}")
def get_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.id == pub_id, Publication.status != "удален").first()
    if not pub:
        raise HTTPException(status_code=404, detail="Текст не найден")
    return pub

# 3. POST: Добавить новый текст и загрузить медиа в MinIO
@router.post("/publications")
def create_publication(
    title: str = Form(...),
    description: str = Form(...),
    genre: str = Form(...),
    avg_length: int = Form(...),
    unique_words_share: str = Form(...),
    image_file: UploadFile = File(...),
    video_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    img_ext = image_file.filename.split('.')[-1]
    vid_ext = video_file.filename.split('.')[-1]
    
    img_filename = f"{uuid.uuid4().hex}.{img_ext}"
    vid_filename = f"{uuid.uuid4().hex}.{vid_ext}"
    
    img_content = image_file.file.read()
    vid_content = video_file.file.read()
    image_file.file.seek(0)
    video_file.file.seek(0)
    
    minio_client.put_object(BUCKET_NAME, img_filename, image_file.file, length=len(img_content), content_type=image_file.content_type)
    minio_client.put_object(BUCKET_NAME, vid_filename, video_file.file, length=len(vid_content), content_type=video_file.content_type)
    
    image_url = f"http://localhost:9002/{BUCKET_NAME}/{img_filename}"
    video_url = f"http://localhost:9002/{BUCKET_NAME}/{vid_filename}"
    
    new_pub = Publication(
        title=title,
        description=description,
        genre=genre,
        avg_length=avg_length,
        unique_words_share=unique_words_share,
        image_url=image_url,
        video_url=video_url,
        status="опубликован",
        creator_id=get_current_user_id() 
    )
    
    db.add(new_pub)
    db.commit()
    db.refresh(new_pub)
    
    return {"message": "Текст успешно добавлен", "id": new_pub.id, "image_url": image_url, "video_url": video_url}

# 4. DELETE: Логическое удаление текста (сырой SQL)
@router.delete("/publications/{pub_id}")
def delete_publication(pub_id: int, db: Session = Depends(get_db)):
    sql_query = text("UPDATE publications SET status = 'удален' WHERE id = :id")
    db.execute(sql_query, {"id": pub_id})
    db.commit()
    return {"message": "Текст успешно удален"}

# ==========================================
# ДОМЕН: М-М (ЗАЯВКИ-УСЛУГИ)
# ==========================================

# 5. POST: Добавить текст в заявку-черновик
@router.post("/requests/items")
def add_item_to_request(publication_id: int, db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    draft_request = db.query(Request).filter(Request.creator_id == user_id, Request.status == "черновик").first()
    
    if not draft_request:
        draft_request = Request(status="черновик", creator_id=user_id)
        db.add(draft_request)
        db.commit()
        db.refresh(draft_request)
        
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Текст не найден")
        
    item = RequestItem(request_id=draft_request.id, publication_id=publication_id)
    db.add(item)
    db.commit()
    return {"message": "Текст успешно добавлен в заявку", "request_id": draft_request.id}

# 6. PUT: Изменение значения в связи м-м (например, ручная корректировка индекса)
@router.put("/requests/items/{publication_id}")
def update_request_item(publication_id: int, custom_index: float = Form(...), db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    draft_request = db.query(Request).filter(Request.creator_id == user_id, Request.status == "черновик").first()
    if not draft_request:
        raise HTTPException(status_code=404, detail="Черновик не найден")
        
    item = db.query(RequestItem).filter(RequestItem.request_id == draft_request.id, RequestItem.publication_id == publication_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Текст в заявке не найден")
        
    item.readability_index = custom_index
    db.commit()
    return {"message": "Индекс текста в заявке обновлен", "new_index": item.readability_index}

# 7. DELETE: Удаление текста из заявки-черновика 
@router.delete("/requests/items/{publication_id}")
def remove_item_from_request(publication_id: int, db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    draft_request = db.query(Request).filter(Request.creator_id == user_id, Request.status == "черновик").first()
    if not draft_request:
        raise HTTPException(status_code=404, detail="Черновик заявки не найден")
        
    item = db.query(RequestItem).filter(RequestItem.request_id == draft_request.id, RequestItem.publication_id == publication_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Текст в заявке не найден")
        
    db.delete(item)
    db.commit()
    return {"message": "Текст успешно удален из заявки"}

# ==========================================
# ДОМЕН: ЗАЯВКИ
# ==========================================

# 8. GET: Получить информацию для иконки корзины
@router.get("/requests/cart-icon")
def get_cart_icon(db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    draft_request = db.query(Request).filter(Request.creator_id == user_id, Request.status == "черновик").first()
    
    if not draft_request:
        return {"request_id": None, "items_count": 0}
    return {"request_id": draft_request.id, "items_count": len(draft_request.items)}

# 9. GET: Список всех заявок с фильтрацией
@router.get("/requests")
def get_requests(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Request).filter(Request.status != "удален", Request.status != "черновик")
    if status:
        query = query.filter(Request.status == status)
        
    requests_list = query.all()
    result = []
    
    for req in requests_list:
        calculated_count = sum(1 for item in req.items if item.readability_index is not None)
        result.append({
            "request_id": req.id, "status": req.status,
            "creator_username": req.creator.username if req.creator else None,
            "created_at": req.created_at, "formed_at": req.formed_at,
            "items_count": len(req.items), "calculated_items_count": calculated_count
        })
    return result

# 10. GET: Просмотреть конкретную заявку со списком текстов
@router.get("/requests/{request_id}")
def get_request_detail(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
        
    items_data = []
    for item in req.items:
        pub = item.publication
        items_data.append({
            "publication_id": pub.id, "title": pub.title,
            "avg_length": pub.avg_length, "unique_words_share": pub.unique_words_share,
            "image_url": pub.image_url, "readability_index": item.readability_index
        })
        
    return {"request_id": req.id, "status": req.status, "created_at": req.created_at, "items": items_data}

# 11. PUT: Редактировать базовые поля заявки (заглушка для доп. полей)
@router.put("/requests/{request_id}")
def update_request_base(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return {"message": "Базовые поля заявки обновлены (если бы они были)"}

# 12. PUT: Сформировать заявку с расчетом индекса читабельности
@router.put("/requests/{request_id}/form")
def form_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if req.status != "черновик":
        raise HTTPException(status_code=400, detail="Можно сформировать только черновик")
    if not req.items:
        raise HTTPException(status_code=400, detail="Заявка пуста")
        
    for item in req.items:
        pub = item.publication
        try: share_val = float(pub.unique_words_share.replace('%', ''))
        except: share_val = 10.0
        
        calc_index = round((pub.avg_length / 100.0) * (1.0 + (share_val / 50.0)), 2)
        item.readability_index = calc_index
        
    req.status = "сформирована"
    req.formed_at = datetime.utcnow()
    db.commit()
    return {"message": "Заявка успешно сформирована", "request_id": req.id, "status": req.status}

# 13. PUT: Завершить заявку модератором
@router.put("/requests/{request_id}/complete")
def complete_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if req.status != "сформирована":
        raise HTTPException(status_code=400, detail="Можно завершить только сформированную заявку")
        
    req.status = "завершена"
    req.completed_at = datetime.utcnow()
    req.moderator_id = 1
    db.commit()
    return {"message": "Заявка завершена", "request_id": req.id, "status": req.status, "completed_at": req.completed_at}

# 14. DELETE: Логическое удаление заявки
@router.delete("/requests/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    req.status = "удален"
    db.commit()
    return {"message": "Заявка логически удалена", "status": req.status}

# ==========================================
# ДОМЕН: ПОЛЬЗОВАТЕЛИ
# ==========================================

# 15. POST: Регистрация пользователя
@router.post("/users/register")
def register_user(username: str = Form(...), first_name: str = Form(None), last_name: str = Form(None), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь существует")
        
    new_user = User(username=username, first_name=first_name, last_name=last_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь зарегистрирован", "user_id": new_user.id}

# 16. POST: Аутентификация (заглушка)
@router.post("/users/login")
def login_user():
    return {"message": "Успешная аутентификация", "token": "dummy_jwt_token_for_lab4"}

# 17. POST: Деавторизация (заглушка)
@router.post("/users/logout")
def logout_user():
    return {"message": "Успешная деавторизация"}