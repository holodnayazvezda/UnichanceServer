from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from schemas.teacher import ResultOfSearchUserId, CreateLessonForm, ResulfOfOperations
from models.user import User
from models.lesson import Lesson


router = APIRouter(prefix="/teacher", tags=["Teacher"])


@router.get("/find_id_from_FIO/{user_email}", response_model=ResultOfSearchUserId)
def find_id_from_FIO(user_email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user = db.query(User).filter(User.email == user_email).first()
    if current_user.status == "guest":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You haven't rights to do this"
        )

    if not user or user.status != 'guest':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not founded"
        )

    return {"id": user.id}


@router.post("/create_lesson", response_model=ResulfOfOperations)
def create_lesson(data: CreateLessonForm, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    if current_user.status == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't rights to do this"
        )
    
    new_lesson = Lesson(
        type_lesson=current_user.lesson_type,
        teacher_id=current_user.id,
        time=data.time,
        place=data.place,
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    

    return {"result": "Lesson is secsessfully added"}


@router.get("/add_child_in_list_lesson/{child_id}/{lesson_id}", response_model=ResulfOfOperations)
def add_child_in_list_lesson(child_id: int, lesson_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.status == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't rights to do this"
        )

    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    lesson.users.append(db.query(User).filter(User.id == child_id).first())
    db.commit()

    return {"result": "secssesfull"}


@router.get("/list_of_your_lection")
def teacher_list_lection(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.status == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't rights to do this"
        )

    lessons_prev = db.query(Lesson).filter(Lesson.teacher_id == current_user.id).all()
    lessons = []

    teacher = db.query(User).filter(User.id == current_user.id).first()

    for lesson in lessons_prev:
        user = db.query(User).filter(User.id == lesson.teacher_id).first()
        lessons.append(
            {
                "time": lesson.time,
                "type_lesson": lesson.type_lesson,
                "teacher_FIO": f"{teacher.surname} {teacher.name} {teacher.patronymic}",
                "place": lesson.place,
                "users":
                    [{
                        "id": user.id,
                        "FIO": f"{user.surname} {user.name} {user.patronymic}",
                        "email": user.email,
                        "photo": user.image_path,
                    }
                        for user in lesson.users]
            }
        )

    return lessons