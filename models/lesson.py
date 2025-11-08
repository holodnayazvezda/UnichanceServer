from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.user import User
from core.database import Base


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    type_lesson = Column(String, nullable=False)

    teacher_id = Column(Integer, ForeignKey(User.id), nullable=False)
    time = Column(String, index=True)
    place = Column(String, index=True, nullable=False)

    users = relationship(User, secondary="lesson_user")
    

lesson_user = Table(
    'lesson_user', Base.metadata,
    Column("id", Integer, primary_key=True),
    Column('lesson_id', Integer, ForeignKey(Lesson.id)),
    Column('user_id', Integer, ForeignKey(User.id))
)