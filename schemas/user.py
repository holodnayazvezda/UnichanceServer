from pydantic import BaseModel, EmailStr
from fastapi import  UploadFile, File

from models.lesson_subject import LessonSubject


class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    password: str
    subject: LessonSubject
    avatar_uuid: str
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    status: str
    subject: LessonSubject
    avatar_uuid: str

    class Config:
        from_attributes = True
