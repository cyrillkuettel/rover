import sys
import unittest
import logging
import numpy as np
from pathlib import Path
from app.plant_box_cropper import PlantBoxCropper
from pandas import DataFrame
from unittest import IsolatedAsyncioTestCase

def get_test_image_directory():
    """ Returns an Operating System agnostic path directory of the test_img. """
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    static = current_file_dir / "static"
    test_img_directory = static / "test_img"
    return test_img_directory


class TestCaseBase(IsolatedAsyncioTestCase):
    def assertIsFile(self, path):
        """ helper function to assert the existence of a file or folder """
        if not Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))


class MyTestCase(TestCaseBase):

    async def test_get_number_of_plant_vase(self):
        Log = logging.getLogger("Test.torch")
        cropper = PlantBoxCropper(
            "https://www.ikea.com/ch/en/images/products/clusia-potted-plant__0634293_pe697503_s5.jpg?f=s",
            get_test_image_directory())
        # Image with 1 potted plant
        box_pred: DataFrame = await cropper.get_pandas_box_predictions()
        plant_vase_rows: DataFrame = await cropper.filter_plant_vase(box_pred)

        self.assertEqual(1, len(plant_vase_rows))

    async def test_get_number_of_plant_vase2(self):
        link = "https://post.healthline.com/wp-content/uploads/2020/05/435791-Forget-You-Have-Plants-11-Types-That" \
               "-Will-Forgive-You_Thumnail-732x549.jpg "
        cropper = PlantBoxCropper(link, get_test_image_directory())  # 2 Plants
        box_pred: DataFrame = await cropper.get_pandas_box_predictions()
        plant_vase = await cropper.filter_plant_vase(box_pred)
        plant_vase_count = len(plant_vase)
        self.assertGreaterEqual(plant_vase_count, 1)

    async def test_get_cropped_image(self):
        cropper = PlantBoxCropper(
            "https://www.ikea.com/ch/en/images/products/clusia-potted-plant__0634293_pe697503_s5.jpg?f=s",
            get_test_image_directory())  # Image
        # with 1 potted plant
        pred: DataFrame = await cropper.get_pandas_box_predictions()
        im = cropper.filter_plant_vase(pred)
        self.assertIsNotNone(im)

    async def test_load_local_image(self):
        """ it is a requirement to use local files """
        root = get_test_image_directory()
        test_image = root / "potted_plant.jpg"
        cropper = PlantBoxCropper(test_image, root)
        im = await cropper.save_and_return_cropped_image()
        Log = logging.getLogger("Test.torch")
        Log.info(type(im))
        self.assertIsNotNone(im)
        self.assertIsInstance(im, np.ndarray)

    async def test_crop_image_and_save(self):
        """ Tests if we can find the bounding box of test_img, get the result np.ndarray and save that to disk"""
        root = get_test_image_directory()
        test_output = root / "cropped_potted_plant.jpg"
        test_input = root / "potted_plant.jpg"

        cropper = PlantBoxCropper(test_input, test_output)
        await cropper.inference_and_save_image()
        # cropped_test_image = root / output
        self.assertIsFile(test_input)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("Test.torch").setLevel(logging.INFO)
    unittest.main()
