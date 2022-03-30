from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class Log(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)