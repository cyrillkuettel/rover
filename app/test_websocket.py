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
    actual_bytes: bytes = await image_as_bytes(plant_img_absolute_path)
    await websocket.send_bytes(actual_bytes)
    await websocket.close()


async def image_as_bytes(path):
    rotated_image = Image.open(path, mode='r')
    img_byte_arr = io.BytesIO()
    rotated_image.save(img_byte_arr, format='JPEG')
    actual_bytes: bytes = img_byte_arr.getvalue()
    return actual_bytes


@pytest.mark.anyio
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

        # image_tools = ImageTools(plant_image_absolute_path)
        # rotation_success = await image_tools.rotate_and_save_image(image_data)
        # assert rotation_success == True

