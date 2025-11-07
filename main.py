import importlib
import uvicorn
import logging.config
from fastapi import FastAPI
from core.database import Base, engine

app = FastAPI(
    title="Unichance API",
    version="1.1.1",
    docs_url='/docs',
    redoc_url='/docs',
    openapi_url='/api-docs'
)
logger = logging.getLogger(__name__)

routers = [
    ("services.ping", "ping_router"),
    ("services.auth", "auth_router"),
]

for module_path, router_name in routers:
    try:
        module = importlib.import_module(module_path)
        router = getattr(module, "router")
        app.include_router(router)
        logger.info(f"Successfully loaded router from {module_path}")
    except Exception as e:
        logger.error(f"Failed to import router from {module_path}: {e}")


Base.metadata.create_all(bind=engine)
logger.info("All database tables created successfully")

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)