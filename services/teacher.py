from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user_status import UserStatus
from schemas.teacher import ResultOfSearchUserId, CreateLessonForm, ResulfOfOperations, LessonCreated
from models.user import User
from models.lesson import Lesson


router = APIRouter(prefix="/teacher", tags=["Teacher"])


@router.get(
    "/find_id_from_FIO/{user_email}",
    response_model=ResultOfSearchUserId,
    summary="Найти ID ученика по email",
    description=(
            "Позволяет преподавателю найти идентификатор ученика по его email. "
            "Доступ запрещён пользователям со статусом 'гость'. "
            "Если пользователь не найден или не является учеником, возвращается ошибка."
    )
)
def find_id_from_FIO(user_email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.email == user_email).first()
    if current_user.status == UserStatus.GUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You haven't rights to do this"
        )

    if not user or user.status != UserStatus.GUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not founded"
        )

    return {"id": user.id}


@router.post(
    "/create_lesson",
    response_model=LessonCreated,
    summary="Создать новый урок",
    description=(
            "Позволяет преподавателю создать новый урок. "
            "В запросе указываются время и место проведения. "
            "Созданный урок автоматически связывается с преподавателем и его предметом. "
            "Доступ запрещён гостям."
    )
)
def create_lesson(
        data: CreateLessonForm,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    if current_user.status == UserStatus.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't rights to do this"
        )

    new_lesson = Lesson(
        subject=current_user.subject,
        teacher_id=current_user.id,
        time=data.time,
        place=data.place,
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return new_lesson


@router.put(
    "/add_child_in_list_lesson/{child_id}/{lesson_id}",
    response_model=ResulfOfOperations,
    summary="Добавить ученика в урок",
    description=(
            "Добавляет ученика с указанным ID в список участников выбранного урока. "
            "Проверяется, что текущий пользователь — владелец урока или суперадминистратор. "
            "В случае успеха возвращает сообщение об успешной операции."
    )
)
def add_child_in_list_lesson(child_id: int, lesson_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.status == UserStatus.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't rights to do this"
        )

    try:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        assert lesson
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    if lesson.teacher_id not in (current_user.id, db.query(User).filter(User.email == "Unichance33@yandex.ru").first().id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This is not your lesson"
        )

    try:
        user = db.query(User).filter(User.id == child_id).first()
        assert user
        lesson.users.append(user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not in list of lesson"
        )

    db.commit()

    return {"result": "secssesfull"}


@router.delete(
    "/delete_child_from_list_lesson/{child_id}/{lesson_id}",
    response_model=ResulfOfOperations,
    summary="Удалить ученика из урока",
    description=(
            "Удаляет ученика с указанным ID из списка участников урока. "
            "Проверяется, что текущий пользователь является владельцем урока или суперадминистратором. "
            "Если ученик не найден в списке — возвращается ошибка."
    )
)
def delete_user_endpoint(child_id: int, lesson_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == child_id).first()

    if current_user.status == UserStatus.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You haven't rights to do this"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    if lesson.teacher_id not in (current_user.id, db.query(User).filter(User.email == "Unichance33@yandex.ru").first().id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This is not your lesson"
        )

    try:
        lesson.users.remove(db.query(User).filter(User.id == child_id).first())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not in list of lesson"
        )

    db.commit()

    return {"result": "User secsessfully delete from lesson"}


@router.get(
    "/list_of_lessons",
    summary="Получить список уроков преподавателя",
    description=(
            "Возвращает все уроки, созданные текущим преподавателем. "
            "Для каждого урока выводится информация о времени, месте, предмете, "
            "ФИО преподавателя и списке учеников. "
            "Доступ запрещён пользователям со статусом 'гость'."
    )
)
def get_list_of_lessons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.status == UserStatus.GUEST:
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
                "id": lesson.id,
                "time": lesson.time,
                "type_lesson": lesson.subject,
                "teacher_FIO": f"{teacher.surname} {teacher.name} {teacher.patronymic}",
                "place": lesson.place,
                "users":
                    [{
                        "id": user.id,
                        "FIO": f"{user.surname} {user.name} {user.patronymic}",
                        "email": user.email,
                        "avatar_uuid": user.avatar_uuid,
                    }
                        for user in lesson.users]
            }
        )

    return lessons
