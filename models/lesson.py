from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from models.lesson_subject import LessonSubject
from models.user import User
from core.database import Base


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    subject = Column(SQLAlchemyEnum(LessonSubject), nullable=False)

    teacher_id = Column(Integer, ForeignKey(User.id), nullable=False)
    time = Column(String)
    place = Column(String, nullable=False)

    users = relationship(User, secondary="lesson_user")
    

lesson_user = Table(
    'lesson_user', Base.metadata,
    Column("id", Integer, primary_key=True),
    Column('lesson_id', Integer, ForeignKey(Lesson.id)),
    Column('user_id', Integer, ForeignKey(User.id))
)