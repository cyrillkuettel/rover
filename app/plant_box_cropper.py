import torch
from pandas import DataFrame
from PIL.Image import Image
import logging
import numpy as np


class PlantBoxCropper:
    """ This class can detect the bounding box of an image, cutting out the desired objects """

    def __init__(self, link):
        self.link = link
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.model.conf = 0.25  # NMS confidence threshold
        self.model.iou = 0.45  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.classes = [58]  # potted plant  (COCO index for class)
        self.model.max_det = 1  # maximum number of detections per image, for now set it to 1 for simplicity
        self.model.amp = False  # Automatic Mixed Precision (AMP) inference

    def get_Number_of_plant_vase(self) -> int:
        number_of_detection_results = len(self.get_pandas_box_predictions())
        return number_of_detection_results

    def get_pandas_box_predictions(self) -> DataFrame:
        results = self.model(self.link)  # inference
        return results.pandas().xyxy[0]  # im predictions (pandas)

    def save_cropped_images(self):
        results = self.model(self.link)  # inference
        results.crop()  # saves the images to the app/runs/detect/exp{%d} directory

    def save_and_return_cropped_image(self) -> np.ndarray:
        results = self.model(self.link)  # inference
        crops = results.crop(save=True)
        img_array = crops[0].get('im')  # crops is a list of dicts
        return img_array

    def filter_plant_vase(self, df: DataFrame) -> DataFrame:
        """ method is not used, as we can just restrict search to potted plant in the __init__ config """
        objects_of_interest = {'potted plant', 'vase'}
        filtered_df = df.loc[df['name'].isin(objects_of_interest)]
        return filtered_df
