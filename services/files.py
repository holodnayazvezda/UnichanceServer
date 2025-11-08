import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from core.database import get_db
from models.file import File as FileModel  # чтобы не пересекалось с fastapi.File

router = APIRouter(prefix="/files", tags=["File API"])

UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload",
    summary="Загрузить изображение",
    description="Загружает изображение на сервер и сохраняет запись в БД.",
    response_model=dict,
)
async def upload_file(
    file: UploadFile = File(..., description="Файл изображения (jpg, png и т.д.)"),
    db: Session = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    unique_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    new_filename = f"{unique_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    abs_path = os.path.abspath(file_path)

    # сохраняем файл
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # сохраняем запись в БД
    db_file = FileModel(
        uuid=unique_id,
        filename=file.filename,
        path=abs_path,
        content_type=file.content_type,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {"uuid": db_file.uuid, "filename": db_file.filename}


@router.get(
    "/{file_uuid}",
    summary="Получить изображение по UUID",
    description="Возвращает изображение по его уникальному идентификатору.",
)
def get_file(file_uuid: str, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.uuid == file_uuid).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(db_file.path),
        media_type=str(db_file.content_type),
        filename=str(db_file.filename),
    )


@router.get(
    "/preview/{file_uuid}",
    summary="Отобразить изображение по UUID",
    description="Отображает изображение по его уникальному идентификатору.",
)
def get_file(file_uuid: str, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.uuid == file_uuid).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    with open(str(db_file.path), "rb") as f:
        image = f.read()
    return Response(content=image, media_type=str(db_file.content_type))


def check_file_exists(file_uuid: str, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.uuid == file_uuid).first()
    return bool(db_file)


