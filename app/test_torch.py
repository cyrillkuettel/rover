import sys
import unittest
import logging
import numpy as np
from pathlib import Path

from PIL.Image import Image

from app.plant_box_cropper import PlantBoxCropper
from pandas import DataFrame


def get_test_image_path():
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    static = current_file_dir / "static"
    test_img = static / "test_img"
    return test_img


class MyTestCase(unittest.TestCase):

    def test_get_number_of_plant_vase(self):
        Log = logging.getLogger("Test.torch")
        cropper = PlantBoxCropper(
            "https://www.ikea.com/ch/en/images/products/clusia-potted-plant__0634293_pe697503_s5.jpg?f=s")
        # Image with 1 potted plant
        box_pred: DataFrame = cropper.get_pandas_box_predictions()
        plant_vase_rows: DataFrame = cropper.filter_plant_vase(box_pred)

        self.assertEqual(1, len(plant_vase_rows))

    def test_get_number_of_plant_vase2(self):
        link = "https://post.healthline.com/wp-content/uploads/2020/05/435791-Forget-You-Have-Plants-11-Types-That" \
               "-Will-Forgive-You_Thumnail-732x549.jpg "
        cropper = PlantBoxCropper(link)  # 2 Plants
        box_pred: DataFrame = cropper.get_pandas_box_predictions()
        plant_vase_count = len(cropper.filter_plant_vase(box_pred))
        self.assertGreaterEqual(plant_vase_count, 1)

    def test_get_cropped_image(self):
        cropper = PlantBoxCropper(
            "https://www.ikea.com/ch/en/images/products/clusia-potted-plant__0634293_pe697503_s5.jpg?f=s")  # Image
        # with 1 potted plant
        im = cropper.filter_plant_vase(cropper.get_pandas_box_predictions())
        self.assertIsNotNone(im)

    def test_load_local_image(self):
        """ it is a requirement to use local files """
        link = get_test_image_path()
        test_image = link / "potted_plant.jpg"
        cropper = PlantBoxCropper(test_image)
        im = cropper.save_and_return_cropped_image()
        Log = logging.getLogger("Test.torch")
        Log.info(type(im))
        self.assertIsNotNone(im)
        self.assertIsInstance(im, np.ndarray)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("Test.torch").setLevel(logging.INFO)
    unittest.main()
