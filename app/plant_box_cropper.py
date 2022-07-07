import torch
from pandas import DataFrame
from PIL.Image import Image
from typing import Dict
import logging
from pathlib import Path
import numpy as np
import cv2


class PlantBoxCropper:
    """ This class uses a yolo object detection model, to cut out the desired objects.  """

    def __init__(self, input_image, output_image: Path):
        self.results = None
        self.input_image = input_image
        self.output_image: Path = output_image
        # self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        # self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', skip_validation=True, force_reload=True)
        self.model = torch.hub.load(repo_or_dir='ultralytics/yolov5', model='yolov5l6', skip_validation=True,
                                    force_reload=True)  # add force_reload=True if fails
        self.model.conf = 0.25  # NMS confidence threshold
        self.model.iou = 0.45  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.classes = [58]  # potted plant  (COCO index for it's class)
        self.model.max_det = 100  # maximum number of detections per image, for now set it to 1 for simplicity
        self.model.amp = False  # Automatic Mixed Precision (AMP) inference

    async def get_num_plant_detection_results(self) -> int:
        pred: DataFrame = await self.get_pandas_box_predictions()
        number_of_detection_results = len(pred)
        return number_of_detection_results

    async def get_pandas_box_predictions(self) -> DataFrame:
        self.results = self.model(self.input_image)  # inference
        return self.results.pandas().xyxy[0]  # im predictions (pandas)

    async def save_cropped_images(self):
        results = self.model(self.input_image)  # inference
        results.crop()  # saves the images to the app/runs/detect/exp{%d} directory

    async def save_and_return_cropped_image(self) -> np.ndarray:
        if not self.results:
            self.results = self.model(self.input_image)  # inference

        crops = self.results.crop(save=True)
        img_array = crops[0].get('im')  # crops is a list of dicts
        return img_array



    async def inference_and_save_image(self):
        """ Note: the results.crop() method already implicitly saves the image to app/runs/detect/exp{%d} The reason
        we save the image manually, is because this way, we have an in-memory reference to the image data. We don't
        have to write a funciton to find the corresponding cropped image in the directory. (Which would be an
        error-prone process ) """

        image = await self.save_and_return_cropped_image()
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Prevent issues with colors flipped after conversion
        from PIL import Image
        img = Image.fromarray(imageRGB)
        img.save(self.output_image)

    async def filter_plant_vase(self, df: DataFrame) -> DataFrame:
        """ method is not used, as we can just restrict search to potted plant in the __init__ config """
        objects_of_interest = {'potted plant', 'vase'}
        filtered_df = df.loc[df['name'].isin(objects_of_interest)]
        return filtered_df

    async def compute_bounding_box_areas(self, df: DataFrame):
        my_dict = {}
        for index, row in df.iterrows():
            xmin = row['xmin']
            xmax = row['xmax']
            ymax = row['ymax']
            ymin = row['ymin']
            width = xmax - xmin
            height = ymax - ymin
            if not width < 0 or height < 0:
                area: float = width*height
                my_dict[index] = area
            else:
                logging.error("AREA IS NEGATIVE")
        return my_dict

    # async def get_right_one(self, bounding_box_areas: list[int], df: DataFrame):
        # the right one is the one where the xmax has the hightest value


