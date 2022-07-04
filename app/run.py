import logging
from pathlib import Path
import pytest
from requests import Response
from plant_api import PlantApiWrapper


def get_test_image_directory():
    """ Returns an Operating System agnostic path directory of the test_img. """
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    static = current_file_dir / "static"
    test_img_directory = static / "test_img"
    return test_img_directory


def main():
    Log = logging.getLogger(__name__)
    root = get_test_image_directory()
    test_image = root / "mint.jpg"
    plantApiWrapper = PlantApiWrapper(test_image)
    response: Response = plantApiWrapper.get_response()
    json_result: dict = plantApiWrapper.json_response(response)
    result_list = json_result['results']
    for item in result_list:
        print(item)
        break


if __name__ == "__main__":
    main()