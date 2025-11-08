from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from core.config import settings
from core.security import get_current_user
from models.user import User
from langchain_gigachat import GigaChat

history_of_messages: Dict[int, List[Dict[str, str]]] = {}

system_prompt = {
    "role": "system",
    "content": "Ты умный помощник в лагере, где детей учат математике, информатике и физике. Отвечай на вопросы просто и понятно."
}

# Инициализация GigaChat
gigachat = GigaChat(
    credentials=settings.API_KEY,
    model="GigaChat-Pro",
    verify_ssl_certs=False
)

router = APIRouter(
    prefix="/unichance-ai",
    tags=["Unichance AI"],
    responses={
        400: {"description": "Неверный запрос"},
        401: {"description": "Неавторизован"},
        500: {"description": "Ошибка при работе с GigaChat"}
    }
)


@router.get(
    "/ask/{prompt}",
    summary="Задать вопрос Unichance AI",
    description=(
        "Отправляет вопрос ИИ и получает ответ. "
        "История диалога сохраняется индивидуально для каждого пользователя."
    ),
    response_description="Ответ от Unichance AI"
)
def ask_unichance_ai(
    prompt: str = Path(..., description="Текст вопроса пользователем", example="Что такое бинарное дерево?"),
    current_user: User = Depends(get_current_user)
):
    """
    Этот метод обращается к GigaChat API с историей сообщений пользователя и возвращает ответ модели.
    """
    if current_user.id not in history_of_messages:
        history_of_messages[current_user.id] = [system_prompt]

    try:
        user_history = history_of_messages[current_user.id]
        user_history.append({"role": "user", "content": prompt})

        # Получаем ответ от модели
        response_text = gigachat.invoke(user_history).content

        if response_text:
            user_history.append({"role": "assistant", "content": response_text})

        return {
            "success": True,
            "answer": response_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {e}")


@router.get(
    "/history",
    summary="Получить историю общения с Unichance AI",
    description=(
        "Возвращает историю сообщений пользователя с возможностью пагинации. "
        "Каждое сообщение содержит роль (`user` или `assistant`) и текст (`content`)."
    ),
    response_model=List[Dict[str, str]],
    response_description="Список сообщений пользователя с AI"
)
def get_history(
    offset: int = Query(
        0,
        ge=0,
        description="Смещение от начала истории сообщений (по умолчанию 0)",
        example=0
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Количество сообщений для возврата (от 1 до 100, по умолчанию 10)",
        example=10
    ),
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает историю общения пользователя с AI с параметрами пагинации.
    """
    if current_user.id not in history_of_messages:
        return []

    user_history = history_of_messages[current_user.id]
    return user_history[offset: offset + limit]
