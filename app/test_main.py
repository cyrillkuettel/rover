from typing import List

import pytest
from fastapi.testclient import TestClient
from .main import app
from .models import TimeType
from sqlalchemy.orm import Session
from .database import Base
from . import models
from sqlalchemy import create_engine

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_number_of_images():
    response = client.get("/number_of_images")
    assert response.json() == {"num": 0}
    assert response.status_code == 200


def test_read_time():
    response = client.get("/api/time")
    result: bool = "not-initialized" in response.text
    assert result == True
