from pathlib import Path

import pytest
from requests import Response

from .plant_api import PlantApiWrapper


def get_test_image_directory():
    """ Returns an Operating System agnostic path directory of the test_img. """
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    static = current_file_dir / "static"
    test_img_directory = static / "test_img"
    return test_img_directory


def test_api_with_potted_plant():
    root = get_test_image_directory()
    test_image = root / "cropped_potted_plant.jpg"
    plant_api = PlantApiWrapper(test_image)
    assert isinstance(plant_api, PlantApiWrapper)


def test_api_class_request_does_not_fail():
    root = get_test_image_directory()
    test_image = root / "mint.jpg"
    plant_api = PlantApiWrapper(test_image)
    res = plant_api.get_response()
    assert res.status_code == 200


def test_species():
    root = get_test_image_directory()
    test_image = root / "mint.jpg"
    plant_api = PlantApiWrapper(test_image)
    response: Response = plant_api.get_response()
    json_result: dict = plant_api.species(response)
    count = 0
    for k, i in json_result.items():
        if "mint" in str(i):
            count = count + 1
    assert count > 0
