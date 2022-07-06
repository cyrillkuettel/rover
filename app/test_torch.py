import sys
import unittest
import logging
import numpy as np
from pathlib import Path
from app import models
from app.main import fill_up_free_space
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
        test_input = root / "potted_plant.jpg"
        test_output = root / "cropped_potted_plant.jpg"

        cropper = PlantBoxCropper(test_input, test_output)
        await cropper.inference_and_save_image()
        # cropped_test_image = root / output
        self.assertIsFile(test_input)

    async def test_two_potted_plant(self):
        """ Tests if we can find the bounding box of test_img, get the result np.ndarray and save that to disk"""
        root = get_test_image_directory()
        test_input = root / "two_potted_plant.jpg"
        test_output = root / "cropped_two_potted_plant.jpg"
        cropper = PlantBoxCropper(test_input, test_output)
        # contain at least two potted_plant, one is bigger than the other
        df: DataFrame = await cropper.get_pandas_box_predictions()
        objects_of_interest = {'potted plant'}
        number_of_potted_plants = len(df.loc[df['name'].isin(objects_of_interest)])
        self.assertEqual(2, number_of_potted_plants)
        Log = logging.getLogger("Test.torch")
        Log.info(df.loc[[0]])
        # the image has a bigger potted plant to the left in the picture. test this
        bounding_boxes_dict = await cropper.compute_bounding_box_areas(df)
        self.assertEqual(2, len(bounding_boxes_dict))
        Log.info(bounding_boxes_dict)

        """ testing the string operations when getting species """

    async def test_string_operations(self):
        maxLen = 11
        plant1 = models.Plant(common_name="Pfefferminze", scientific_name="Mentha × piperita")
        common_names = [plant1.common_name]
        scientific_names = [plant1.scientific_name]
        modified_common_names, modified_scientific_names = await fill_up_free_space(common_names, maxLen,
                                                                                    scientific_names)
        self.assertEqual(11, len(modified_common_names))
        self.assertEqual(11, len(modified_scientific_names))
        self.assertEqual("", modified_scientific_names[10])
        self.assertEqual("", modified_common_names[10])
        self.assertEqual("", modified_common_names[1])

    async def test_query_plants(self):
        plant1 = models.Plant(absolute_path="foo1", common_name="Pfefferminze", scientific_name="Mentha × piperita")
        plant2 = models.Plant(absolute_path="foo2")
        plant3 = models.Plant(absolute_path="foo3", common_name="Pfefferminze2", scientific_name="Mentha × piperita2")
        plants = [plant1, plant2, plant3]

        common_names: list[str] = [plant.common_name if plant.common_name else "" for plant in plants]
        scientific_names: list[str] = [plant.scientific_name if plant.common_name else "" for plant in plants]
        self.assertEqual(["Pfefferminze", "", "Pfefferminze2"], common_names)
        self.assertEqual(["Mentha × piperita", "", "Mentha × piperita2"], scientific_names)




if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("Test.torch").setLevel(logging.INFO)
    unittest.main()
