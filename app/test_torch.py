import sys
import unittest
import logging
import numpy as np
from pathlib import Path
from app import models
from app.main import determine_similar_Plant
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

        """ testing duplicates filtering methods """

    async def test_find_matching_plant_with_duplicate_attribute(self):
        plant1 = models.Plant(absolute_path="foo1", common_name="Pfefferminze", scientific_name="foo", is_first=False)
        plant2 = models.Plant(absolute_path="foo1", common_name="Pfefferminze", scientific_name="bar", is_first=True)
        plant3 = models.Plant(absolute_path="foo1", common_name="Something", scientific_name="foobar", is_first=False)
        plants = [plant1, plant2, plant3]
        candidates_list = await determine_similar_Plant(plants)
        result: models.Plant = candidates_list[0]
        Log = logging.getLogger("Test.torch")
        self.assertEqual(plant2.common_name, result.common_name)

    async def test_duplicates_if_no_match_just_get_random(self):
        plant1 = models.Plant(absolute_path="foo1", common_name="Pfefferminze", scientific_name="foo", is_first=False)
        plant2 = models.Plant(absolute_path="foo1", common_name="Trauben", scientific_name="bar", is_first=True)
        plant3 = models.Plant(absolute_path="foo1", common_name="Basilikum", scientific_name="foobar", is_first=False)
        plants = [plant1, plant2, plant3]
        candidates_list = await determine_similar_Plant(plants)
        self.assertEquals(len(candidates_list), 0)

        """ If multiple available, pick the one which does no come immediatly after"""

    async def test_if_multiple_possible_candidates_get_oldest(self):
        plant0 = models.Plant(id=1, absolute_path="plant0", common_name="Pfefferminze", scientific_name="foo",
                              is_first=True)
        plant1 = models.Plant(id=2, absolute_path="plant1", common_name="Pfefferminze", scientific_name="bar",
                              is_first=False)
        plant2 = models.Plant(id=3, absolute_path="plant2", common_name="Something", scientific_name="foobar",
                              is_first=False)
        plant3 = models.Plant(id=4, absolute_path="plant3", common_name="SomethingOther", scientific_name="foobar",
                              is_first=False)
        plant4 = models.Plant(id=5, absolute_path="plant4", common_name="Pfefferminze", scientific_name="foobar",
                              is_first=False)

        plants = [plant0, plant1, plant2, plant3, plant4]

        candidates_list = await determine_similar_Plant(plants)
        result = candidates_list[0]
        self.assertEqual("plant4", result.absolute_path)
        self.assertEqual(plant4.common_name, result.common_name)


""" same as before but empty """

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("Test.torch").setLevel(logging.INFO)
    unittest.main()
