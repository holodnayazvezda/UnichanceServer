from sqlalchemy import Column, Integer, String
from core.database import Base
import uuid

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
