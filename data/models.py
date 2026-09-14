# data/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    
    # Связи (без каскадного удаления по ТЗ)
    publications = relationship("Publication", back_populates="creator")
    likes = relationship("Like", back_populates="user")

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="черновик") # черновик, опубликован, удален
    
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    
    genre = Column(String, nullable=True)

    # Поля по предметной области (Читабельность)
    avg_length = Column(Integer, nullable=True)
    unique_words_share = Column(String, nullable=True)
    
    # Системные поля по ТЗ
    created_at = Column(DateTime, default=datetime.utcnow)
    formed_at = Column(DateTime, nullable=True)
    
    # Внешний ключ на создателя
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    # Связи
    creator = relationship("User", back_populates="publications")
    likes = relationship("Like", back_populates="publication")

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    # По ТЗ: первичный и два внешних ключа, без каскадного удаления
    user_id = Column(Integer, ForeignKey("users.id"))
    publication_id = Column(Integer, ForeignKey("publications.id"))
    
    # Связи
    user = relationship("User", back_populates="likes")
    publication = relationship("Publication", back_populates="likes")