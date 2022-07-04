import json
import logging
from pathlib import Path
import requests
from app import constants


class PlantApiWrapper:
    def __init__(self, image):
        self.plantIDkey = constants.Constants().api_key
        self.image: Path = image
        self.api_endpoint = f"https://my-api.plantnet.org/v2/identify/all?api-key={self.plantIDkey}"

    def species(self, response):
        json_result = json.loads(response.text)
        return json_result

    def get_response(self):
        image_path = str(self.image.resolve())
        logging.info(image_path)
        image_data = open(image_path, 'rb')
        data = {
            'organs': ['leaf']
        }
        files = [
            ('images', (image_path, image_data)),
        ]
        req = requests.Request('POST', url=self.api_endpoint, files=files, data=data)
        prepared = req.prepare()

        s = requests.Session()
        response = s.send(prepared)
        return response


