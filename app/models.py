from sqlalchemy import Column, Integer, String, Enum, Boolean
from .database import Base
import enum


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)

    def __str__(self):
        return self.content


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    is_first = Column(Boolean)  # first or not
    absolute_path = Column(String)
    scientific_name = Column(String)
    common_name = Column(String)

    def __str__(self):
        return '{}, {}, {}'.format(self.absolute_path, self.scientific_name, self.common_name)


class TimeType(enum.Enum):
    startTime = 0  # number is not relevant
    stopTime = 1


class Time(Base):
    __tablename__ = "time"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(String)
    description = Column(Enum(TimeType))

    def __str__(self):
        return self.time


class PlantInRow(Base):
    __tablename__ = "plantinrow"
    id = Column(Integer, primary_key=True, index=True)
    position = Column(String)
