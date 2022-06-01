
from sqlalchemy import Column, Integer, String
from .database import Base


class Log(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)

    def __str__(self):
        return self.content


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    absolute_path = Column(String)

    def __str__(self):
        return self.absolute_path


class Time(Base):
    __tablename__ = "time"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(String)

    def __str__(self):
        return self.time
