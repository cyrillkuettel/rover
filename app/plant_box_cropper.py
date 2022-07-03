import torch
from pandas import DataFrame
from PIL.Image import Image
import logging
from pathlib import Path
import numpy as np
import cv2


class PlantBoxCropper:
    """ This class can detect the bounding box of an image, cutting out the desired objects """

    def __init__(self, input_image, output: Path):
        self.input_image = input_image
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.model.conf = 0.25  # NMS confidence threshold
        self.model.iou = 0.45  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.classes = [58]  # potted plant  (COCO index for it's class)
        self.model.max_det = 1  # maximum number of detections per image, for now set it to 1 for simplicity
        self.model.amp = False  # Automatic Mixed Precision (AMP) inference
        self.output_image: Path = output  # the path where we save the outputs

    def get_num_plant_detection_results(self) -> int:
        number_of_detection_results = len(self.get_pandas_box_predictions())
        return number_of_detection_results

    def get_pandas_box_predictions(self) -> DataFrame:
        results = self.model(self.input_image)  # inference
        return results.pandas().xyxy[0]  # im predictions (pandas)

    def save_cropped_images(self):
        results = self.model(self.input_image)  # inference
        results.crop()  # saves the images to the app/runs/detect/exp{%d} directory

    def save_and_return_cropped_image(self) -> np.ndarray:
        results = self.model(self.input_image)  # inference
        crops = results.crop(save=True)
        img_array = crops[0].get('im')  # crops is a list of dicts
        return img_array

    def save_image(self):
        """ Note: the results.crop() method already implicitly saves the image to app/runs/detect/exp{%d} The reason
        we save the image manually, is because this way, we have an in-memory reference to the image data. We don't
        have to write a funciton to find the corresponding cropped image in the directory. (Which would be an
        error-prone process ) """

        image = self.save_and_return_cropped_image()
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Prevent issues with colors flipped after conversion
        from PIL import Image
        img = Image.fromarray(imageRGB)
        img.save(self.output_image)

    def filter_plant_vase(self, df: DataFrame) -> DataFrame:
        """ method is not used, as we can just restrict search to potted plant in the __init__ config """
        objects_of_interest = {'potted plant', 'vase'}
        filtered_df = df.loc[df['name'].isin(objects_of_interest)]
        return filtered_df
