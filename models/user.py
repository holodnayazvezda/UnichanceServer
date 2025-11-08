from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from core.database import Base
from models.lesson_subject import LessonSubject
from models.user_status import UserStatus


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    patronymic = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    status = Column(SQLAlchemyEnum(UserStatus))
    subject = Column(SQLAlchemyEnum(LessonSubject))
    avatar_uuid = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
