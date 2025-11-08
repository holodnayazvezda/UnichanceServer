from sqlalchemy import Column, Integer, String
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    surname = Column(String(100), index=True)
    patronymic = Column(String(100), index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(100), index=True)
    lesson_type = Column(String(100), index=True)
    avatar_uuid = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
