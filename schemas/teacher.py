from pydantic import BaseModel

from models.lesson import Lesson
from models.lesson_subject import LessonSubject


class ResultOfSearchUserId(BaseModel):
    id: int


class ResulfOfOperations(BaseModel):
    result: str
    

class CreateLessonForm(BaseModel):
    time: str
    place: str

class LessonCreated(BaseModel):
    id: int
    subject: LessonSubject
    teacher_id: int
    time: str
    place: str