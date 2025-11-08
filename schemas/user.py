from pydantic import BaseModel, EmailStr
from fastapi import  UploadFile, File

class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    password: str
    lesson_type: str
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
    lesson_type: str
    avatar_uuid: str

    class Config:
        from_attributes = True
