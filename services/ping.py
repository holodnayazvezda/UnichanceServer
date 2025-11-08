from fastapi import APIRouter

router = APIRouter(prefix="/ping", tags=["Ping"])

@router.get(
    "/",
    summary="Проверка доступности сервера",
    description=(
        "Простой эндпоинт для проверки работы и доступности API. "
        "Возвращает ответ `{ 'message': 'Pong' }`, если сервер функционирует корректно."
    )
)
async def ping():
    return {"message": "Pong"}
