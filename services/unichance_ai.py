from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import settings
from core.security import get_current_user
from models.user import User
from langchain_gigachat import GigaChat

history_of_messages = {}
system_prompt = {"role": "system", "content": "Ты умный помощник в лагере, где детей учат математике, информатики, физике и физике. отвечай на вопросы просто и понятно."}
gigachat = GigaChat(
    credentials=settings.API_KEY,
    model="GigaChat-Pro",
    verify_ssl_certs=False
)

model = 'gpt-5'

router = APIRouter(prefix='/unichance-ai', tags=['Unichance ai'])

@router.get('/ask/{prompt}')
def ask_unichance_ai(prompt: str,  current_user: User = Depends(get_current_user)):
    if current_user.id not in history_of_messages:
        history_of_messages[current_user.id] = []

    try:
        users_dialog_history = history_of_messages[current_user.id]
        users_dialog_history.append({"role": "user", "content": prompt})
        response_text = gigachat.invoke(users_dialog_history).content
        if response_text:
            users_dialog_history.append({'role': 'assistant', 'content': response_text})
        return {
            "success": True,
            "answer": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/history', response_model=List[Dict[str, str]])
def get_history(
    offset: int = Query(0, ge=0, description="Смещение для истории сообщений"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество сообщений для возврата"),
    current_user: User = Depends(get_current_user)
):
    if current_user.id not in history_of_messages:
        return []

    user_history = history_of_messages[current_user.id]
    return user_history[offset : offset + limit]
