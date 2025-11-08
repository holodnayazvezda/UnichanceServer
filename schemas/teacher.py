from pydantic import BaseModel


class ResultOfSearchUserId(BaseModel):
    id: int


class ResulfOfOperations(BaseModel):
    result: str
    

class CreateLessonForm(BaseModel):
    time: str
    place: str