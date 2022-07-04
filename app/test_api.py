import logging
from pathlib import Path

import pytest
from requests import Response

from .plant_api import PlantApiWrapper

Log = logging.getLogger(__name__)


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
    res = plant_api.do_request()
    assert res.status_code == 200


def test_species_contains_mint_somewhere():
    root = get_test_image_directory()
    test_image = root / "mint.jpg"
    plantApiWrapper = PlantApiWrapper(test_image)
    response: Response = plantApiWrapper.do_request()
    json_result: dict = plantApiWrapper.json_response(response)
    count = 0
    for k, i in json_result.items():
        if "mint" in str(i):
            count = count + 1
    assert count > 0


def test_max_score_is_correct():
    root = get_test_image_directory()
    test_image = root / "mint.jpg"
    plantApiWrapper = PlantApiWrapper(test_image)
    response: Response = plantApiWrapper.do_request()
    json_result: dict = plantApiWrapper.json_response(response)
    maximum_score = plantApiWrapper.get_max_score(json_result)
    expected: float = 0.12117
    assert expected == maximum_score


def test_get_best_result():
    root = get_test_image_directory()
    test_image = root / "mint.jpg"
    plantApiWrapper = PlantApiWrapper(test_image)
    response: Response = plantApiWrapper.do_request()
    json_result: dict = plantApiWrapper.json_response(response)
    best_result = plantApiWrapper.get_result_with_max_score(json_result)
    species = best_result["species"]
    commonName: list = species["commonNames"]
    assert species["scientificNameWithoutAuthor"] == "Mentha x verticillata"
    assert "Whorled Mint" in commonName

