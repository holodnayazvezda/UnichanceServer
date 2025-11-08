from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.lesson import Lesson
from models.user_status import UserStatus

router = APIRouter(
    prefix="/guest",
    tags=["Guest"]
)

@router.get(
    "/my_lessons",
    summary="Получить список уроков гостя",
    description=(
        "Возвращает все уроки, на которые записан текущий пользователь со статусом 'гость'. "
        "Если пользователь не является гостем, возвращает ошибку 403. "
        "В ответе содержится информация об уроках, включая время, предмет, место и ФИО преподавателя."
    )
)
def get_my_lessons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.status != UserStatus.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only guests can access this endpoint"
        )

    lessons = db.query(Lesson).join(Lesson.users).filter(User.id == current_user.id).all()

    result = []
    for lesson in lessons:
        teacher = db.query(User).filter(User.id == lesson.teacher_id).first()
        result.append({
            "id": lesson.id,
            "time": lesson.time,
            "type_lesson": lesson.subject,
            "teacher_FIO": f"{teacher.surname} {teacher.name} {teacher.patronymic}" if teacher else None,
            "place": lesson.place
        })

    return result
