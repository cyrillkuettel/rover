import torch
from pandas import DataFrame
from PIL.Image import Image
import logging


# notes:
# model.conf has some interesting attributes
# https://github.com/ultralytics/yolov5/issues/36

class PlantBoxCropper:
    """ This class can detect the bounding box of an image, cutting out potted_plant / vase objects """

    def __init__(self, link: str):
        self.link = link

    def get_Number_Of_plant_vase(self) -> int:
        number_of_detection_results = len(self.get_pandas_box_predictions())
        return number_of_detection_results

    def get_pandas_box_predictions(self) -> DataFrame:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        results = model(self.link)  # inference
        return results.pandas().xyxy[0]  # im predictions (pandas)

    def save_cropped_images(self):
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        results = model(self.link)  # inference
        results.crop() # saves the images to the app/runs/detect directory

    def filter_plant_vase(self, df: DataFrame) -> DataFrame:
        objects_of_interest = {'potted plant', 'vase'}
        filtered_df = df.loc[df['name'].isin(objects_of_interest)]
        return filtered_df

    def filter_plant(self, df: DataFrame) -> DataFrame:
        objects_of_interest = {'potted plant'}
        filtered_df = df.loc[df['name'].isin(objects_of_interest)]
        return filtered_df
