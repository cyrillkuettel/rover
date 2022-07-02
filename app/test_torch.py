import sys
import unittest
import logging
from pathlib import Path

from app.PlantBoxCropper import PlantBoxCropper
from pandas import DataFrame


class MyTestCase(unittest.TestCase):

    def test_get_number_of_plant_vase(self):
        Log = logging.getLogger("Test.torch")
        cropper = PlantBoxCropper(
            "https://www.ikea.com/ch/en/images/products/clusia-potted-plant__0634293_pe697503_s5.jpg?f=s")  # Image with 1 potted plant
        box_pred: DataFrame = cropper.get_pandas_box_predictions()
        plant_vase_rows: DataFrame = cropper.filter_plant_vase(box_pred)

        self.assertEqual(2, len(plant_vase_rows))

    def test_get_number_of_plant_vase2(self):
        cropper = PlantBoxCropper(  # 2 Plants
            "https://post.healthline.com/wp-content/uploads/2020/05/435791-Forget-You-Have-Plants-11-Types-That-Will-Forgive-You_Thumnail-732x549.jpg")
        box_pred: DataFrame = cropper.get_pandas_box_predictions()
        plant_vase_count = len(cropper.filter_plant_vase(box_pred))
        plant_count = len(cropper.filter_plant(box_pred))
        self.assertGreaterEqual(plant_vase_count, 2)

    def test_get_cropped_image(self):
        cropper = PlantBoxCropper(
            "https://www.ikea.com/ch/en/images/products/clusia-potted-plant__0634293_pe697503_s5.jpg?f=s")  # Image with 1 potted plant
        im = cropper.filter_plant_vase(cropper.get_pandas_box_predictions())
        self.assertIsNotNone(im)

    def test_random_image(self):
        link = "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/bus.jpg"
        cropper = PlantBoxCropper(link)
        cropper.save_cropped_images()
        self.assertTrue(True)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("Test.torch").setLevel(logging.INFO)
    unittest.main()
