import importlib
import uvicorn
import logging.config
from fastapi import FastAPI
from core.database import Base, engine
from fastapi.staticfiles import StaticFiles

from models.lesson_subject import LessonSubject
from models.user_status import UserStatus

app = FastAPI(
    title="Unichance API",
    version="1.1.1",
    docs_url='/docs',
    redoc_url='/docs',
    openapi_url='/api-docs'
)
app.mount("/static", StaticFiles(directory="static"), name="static")
logger = logging.getLogger(__name__)

routers = [
    ("services.ping", "ping_router"),
    ("services.auth", "auth_router"),
    ("services.superadmin", "superadmin_router"),
    ("services.teacher", "teacher_router"),
    ("services.files", "file_router"),
    ("services.guest", "guest_router"),
]

for module_path, router_name in routers:
    try:
        module = importlib.import_module(module_path)
        router = getattr(module, "router")
        app.include_router(router)
        logger.info(f"Successfully loaded router from {module_path}")
    except Exception as e:
        logger.info(f"Failed to import router from {module_path}: {e}")


Base.metadata.create_all(bind=engine)
logger.info("All database tables created successfully")


from core.database import SessionLocal
from core.security import hash_password
from models.user import User


with SessionLocal() as db:
    if not db.query(User).filter(User.email == "Unichance33@yandex.ru").first():
        new_user = User(
            name="Галина",
            surname="Повилайнен",
            patronymic="Вольдемаровна",
            email="Unichance33@yandex.ru",
            password_hash=hash_password("Unichance33"),
            status=UserStatus.SUPERADMIN,
            avatar_uuid="",
            subject=LessonSubject.UNICHANCE
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)


if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=1488)