from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket
from .main import app
import io
from .main import ImageTools
from PIL import Image

client = TestClient(app)


def get_test_image_path():
    """ Returns an Operating System agnostic path of the test image. """
    test_img = get_test_image_dir()
    return test_img / "potted_plant.jpg"


def get_test_image_dir():
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    static = current_file_dir / "static"
    test_img = static / "test_img"
    return test_img


STATIC_IMG = get_test_image_dir()


@app.websocket_route("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    plant_img_absolute_path = get_test_image_path()
    image_tools = ImageTools(plant_img_absolute_path)
    actual_bytes: bytes = await image_tools.image_as_bytes()
    await websocket.send_bytes(actual_bytes)
    await websocket.close()


def test_websocket():
    testclient = TestClient(app)
    number_of_plants = 0
    with testclient.websocket_connect("/ws") as websocket:
        plant_image_absolute_path: Path = STATIC_IMG / f"original_plant{number_of_plants}.jpg"
        image_data: bytes = websocket.receive_bytes()
        if image_data is None:
            bool = False
        else:
            bool = True
        assert bool == True

