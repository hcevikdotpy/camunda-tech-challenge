from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

from pydantic import BaseModel

Base = declarative_base()


# db models
class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True, index=True)
    animal_type = Column(String, index=True)
    file_path = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# pydantic models
class SavePicturesRequest(BaseModel):
    animal_type: str
    number_of_pictures: int
