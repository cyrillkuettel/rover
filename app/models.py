from sqlalchemy import Column, Integer, String, Enum
from .database import Base
import enum


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


class TimeType(enum.Enum):
    startTime = 0
    stopTime = 1


class Time(Base):
    __tablename__ = "time"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(String)
    description = Column(Enum(TimeType))  # time is either startTime or endTime, represented as Enum

    def __str__(self):
        return self.time
