import torch
from pandas import DataFrame
from PIL.Image import Image
import logging


class PlantBoxCropper:
    """ This class can detect the bounding box of an image, cutting out potted_plant / vase objects """

    def __init__(self, link):
        self.link = link
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.model.conf = 0.25  # NMS confidence threshold
        self.model.iou = 0.45  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.classes = [58]  # COCO index for potted plant (object of interest)
        self.model.max_det = 1  # maximum number of detections per image, for now set it to 1
        self.model.amp = False  # Automatic Mixed Precision (AMP) inference

    def get_Number_Of_plant_vase(self) -> int:
        number_of_detection_results = len(self.get_pandas_box_predictions())
        return number_of_detection_results

    def get_pandas_box_predictions(self) -> DataFrame:
        results = self.model(self.link)  # inference
        return results.pandas().xyxy[0]  # im predictions (pandas)

    def save_cropped_images(self):
        results = self.model(self.link)  # inference
        results.crop()  # saves the images to the app/runs/detect directory

    def filter_plant_vase(self, df: DataFrame) -> DataFrame:
        objects_of_interest = {'potted plant', 'vase'}
        filtered_df = df.loc[df['name'].isin(objects_of_interest)]
        return filtered_df
