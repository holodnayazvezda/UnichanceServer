from fastapi import APIRouter

router = APIRouter(prefix="/ping", tags=["Ping"])

@router.get("/")
async def ping():
    return {"message": "Pong"}