from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, Depends, HTTPException
from typing import List, Union, Tuple, Any
from pathlib import Path
import logging
from string import Template
from datetime import datetime, timedelta
import subprocess
from pandas import DataFrame
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
from requests import Response

from .models import TimeType, Time
from .plant_api import PlantApiWrapper
from .plant_box_cropper import PlantBoxCropper
from .socket_manager import ConnectionManager
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session, Query
import torch
from pydantic import BaseSettings
from sqlalchemy import update

models.Base.metadata.create_all(bind=engine)


class Settings(BaseSettings):
    openapi_url: str = ""  # disable OpenAPI docs


settings = Settings()
app = FastAPI(openapi_url=settings.openapi_url)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_file = Path(__file__)
current_file_dir = current_file.parent  # /code/app
TEMPLATES = current_file_dir / "templates"
UPLOAD = current_file_dir / "upload"
APP = UPLOAD / "app-release.apk"
static = current_file_dir / "static"
STATIC_IMG = static / "img"
TEST_IMG = static / "test_img"
IMG_REMOVE = STATIC_IMG / "remove-images.sh"
FAVICON = STATIC_IMG / "favicon.ico"

templates = Jinja2Templates(directory=TEMPLATES)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s %(processName)s %(threadName)s', )


class Paths:
    def __init__(self):
        self.pilot_apk_name = "app-release.apk"

    def get_pilot_apk_name(self):
        return self.pilot_apk_name


manager = ConnectionManager()
paths = Paths()

websocket_map = {}  # This is used to get websocket object by id


# Helper function to access the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DeltaTemplate(Template):
    delimiter = "%"


async def getStopTime(db: Session):
    """ Returns the Time difference in seconds """
    startTimeColumn: List[Time] = db.query(Time).filter_by(description=TimeType.startTime).all()
    stopTimeColumn: List[Time] = db.query(Time).filter_by(description=TimeType.stopTime).all()

    if len(stopTimeColumn) > 0 and len(startTimeColumn) > 0:
        startTime = startTimeColumn[0].time
        stopTime = stopTimeColumn[0].time
        startTimeDateTime = datetime.fromtimestamp(int(startTime) / 1000.0)
        stopTimeDateTime = datetime.fromtimestamp(int(stopTime) / 1000.0)
        diffDateTime = stopTimeDateTime - startTimeDateTime
        return strfdelta(diffDateTime, '%M:%S')
    else:
        logging.error("error stopTimeColumn or startTimeColumn is not correct")


def strfdelta(delta: timedelta, fmt):
    d = {"D": delta.days}
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


@app.get("/api/time")
async def time(db: Session = Depends(get_db)):
    stopTimeColumn: List[str] = db.query(models.Time).filter_by(description=TimeType.stopTime).all()
    if len(stopTimeColumn) > 0:
        displayTime = stopTimeColumn[0]
    else:
        startTimeColumn: List[str] = db.query(models.Time).filter_by(description=TimeType.startTime).all()
        if len(startTimeColumn) > 0:
            displayTime = startTimeColumn[0]
        else:
            displayTime = "not-initialized"
        logging.info(f"fetched time = %s", displayTime)
    return displayTime


@app.get("/time")
async def time(db: Session = Depends(get_db)):
    t = db.query(models.Time).all()
    return t




@app.get("/api/plantnames/{plant_id}")
async def common_name(plant_id: int, db: Session = Depends(get_db)):
    _id = str(plant_id)
    absol_path: Path = STATIC_IMG / f"plant{_id}.jpg"
    absolute_path_str = str(absol_path.resolve())
    logging.info(f"absolute_path_str = {absolute_path_str}")
    plant_object: List[models.Plant] = db.query(models.Plant).filter_by(absolute_path=absolute_path_str).all()
    if not plant_object:
        logging.error("empty list returned")
        return {"common_name": "",
                "scientific_name": ""}
    _common_name = plant_object[0].common_name
    _scientific_name = plant_object[0].scientific_name
    return {"common_name": _common_name,
            "scientific_name": _scientific_name}


@app.get("/")
async def main(request: Request, db: Session = Depends(get_db)):
    plants: List[Query] = await get_plants_from_db(db)

    logs: List[Query] = await get_logs_from_db(db)

    number_of_plants: int = len(plants)

    current_time = "0:00"
    if timeAlreadyStopped(db):  # display the stopped time if it exists
        current_time = await getStopTime(db)

    return templates.TemplateResponse(
        "index.html", {"request": request,
                       "Log": logs,
                       "numer_of_images": number_of_plants,
                       "time": current_time,
                       "plants": plants,
                       "images_for_future": 12 - number_of_plants})  # expecting never more than 11 plant


async def get_first_plant_identification_result(db):
    absol_path: Path = STATIC_IMG / f"plant0.jpg"
    absolute_path_str = str(absol_path.resolve())
    plant_object: List[models.Plant] = db.query(models.Plant).filter_by(absolute_path=absolute_path_str).all()
    common_nameID0 = ""
    scientific_name_ID0 = ""
    if plant_object:
        common_nameID0 = f"Gemeiner Name: {plant_object[0].common_name}"
        scientific_name_ID0 = f"Wissenschaftlicher Name: {plant_object[0].scientific_name}"
    return common_nameID0, scientific_name_ID0


async def get_logs_from_db(db):
    return db.query(models.Log).all()


async def get_plants_from_db(db):
    return db.query(models.Plant).all()


@app.get("/number_of_images")
async def delete_cache(request: Request, db: Session = Depends(get_db)):
    num = await get_num_plants_in_db(db)
    return {"num": num}

"""
@app.get("/clear", response_class=HTMLResponse)
async def delete_cache(request: Request, db: Session = Depends(get_db)):
    await clear_database(db)
    logging.info("clearing the images")
    logging.info(f"calling script {IMG_REMOVE}")
    subprocess.call(IMG_REMOVE)
    return "<h2>Cleared Cache. </h2>"
"""



@app.get("/steam/injector/restart/")
async def restart():
    logging.info("triggered steam/injector/restart")
    _id = 777
    if _id in websocket_map:
        try:
            pilot: WebSocket = websocket_map.get(_id)
            await manager.send_personal_message("restart", pilot)
        except Exception:
            logging.info("FAILED TO STOP")
            try:
                pilot: WebSocket = websocket_map.get(_id)
                await manager.send_personal_message("restart", pilot)
            except Exception:
                logging.info("FAILED TO STOP")


@app.get("/steam/injector/stop/")
async def stop(db: Session = Depends(get_db)):
    logging.info("triggered steam/injector/stop")
    _id = 777
    if _id in websocket_map:
        pilot: WebSocket = websocket_map.get(_id)
        try:
            await manager.send_personal_message("jetzt_stop", pilot)
        except Exception as ex:
            logging.info(ex)
            logging.info("FAILED TO STOP")


    import asyncio
    # await asyncio.sleep(5)  # wait for the results to load in the background
    # find if some plants are the same species
    plant_objects: List[models.Plant] = db.query(models.Plant).all()
    candidates_list = await determine_similar_Plant(plant_objects)
    if not candidates_list:
        import random
        logging.info("gamble")
        plant_in_row = random.randint(1, 5)
    else:
        plant_in_row = candidates_list[0].id - 1
    logging.info(f"Die gleiche Pflanze ist an {plant_in_row}. Stelle im Zielbereich")
    plantinrow = models.PlantInRow(position=plant_in_row)
    db.add(plantinrow)
    db.commit()

@app.get("/position")
async def position(db: Session = Depends(get_db)):
    plant_position: List[models.PlantInRow] = db.query(models.PlantInRow).all()
    if plant_position:
        return plant_position[0]
    else:
        return "_"



@app.get("/plants")
async def p(db: Session = Depends(get_db)):
    plant_objects: List[models.Plant] = db.query(models.Plant).all()
    return plant_objects


async def determine_similar_Plant(plant_objects: List[models.Plant]) -> List[models.Plant]:
    logging.info("determin similar plant")
    from collections import Counter
    common_names = [p.common_name for p in plant_objects]
    # get duplicates.
    dups = [k for k, v in Counter(common_names).items() if v > 1]
    scientifc_names = [p.scientific_name for p in plant_objects]
    scientifc_names_duplicates = [k for k, v in Counter(scientifc_names).items() if v > 1]
    if not dups:
        return list()  # return empty list if not duplicates have been found
    candidates = [p for p in plant_objects if p.common_name in dups]
    if len(candidates) == 1:  # this case is easy, only one possibility
        return candidates
    else:  # get the one with the highest index
        try:
            current_id = -1
            max_obj = None
            for plant in candidates:
                if plant.id > current_id:
                    current_id = plant.id
                    max_obj = plant
            return [max_obj]
        except Exception:
            return candidates[0]


async def clear_database(db: Session):
    db.query(models.Plant).delete()
    db.query(models.Time).delete()
    db.query(models.Log).delete()
    logging.info("cleared database")


def timeAlreadySet(db):
    timeColumn: int = len(db.query(models.Time).all())
    return timeColumn > 0


def timeAlreadyStopped(db: Session):
    timeColumn: int = db.query(models.Time).count()
    return timeColumn >= 2  # if the time has stopped, we have exatly two Time objects in db


async def isMessageFromApp(client_id: int):
    # indicates message from app (arbitrary defined range)
    return len(str(client_id)) <= 9


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            if client_id == 777:
                websocket_map[client_id] = websocket
            if client_id == 888:
                number_of_plants = await get_num_plants_in_db(db)
                logging.info(f"number_of_plants in db: {number_of_plants}")
                plant_image_absolute_path: Path = STATIC_IMG / f"original_plant{number_of_plants}.jpg"
                image_tools = ImageTools(plant_image_absolute_path)
                image_data: bytes = await websocket.receive_bytes()
                logging.info(f"Received bytes. Length = {len(image_data)}")
                rotation_success = await image_tools.rotate_and_save_image(image_data)
                if not rotation_success:
                    logging.error("rotation failed")
                    continue
                try:
                    img_byte_arr = await image_tools.convert_if_necessary()
                    img_byte_arr = img_byte_arr.getvalue()
                except Exception as ex:
                    logging.error(
                        f"Something Failed with image_tools.convert_if_necessary: {plant_image_absolute_path}")
                    logging.info(ex)
                    continue
                try:
                    plant_image_cropped_path: Path = STATIC_IMG / f"plant{number_of_plants}.jpg"
                    cropper = PlantBoxCropper(
                        input_image=plant_image_absolute_path,
                        output_image=plant_image_cropped_path
                    )
                    num_detection_results = await cropper.get_num_plant_detection_results()
                    if num_detection_results > 0:
                        logging.info("found > 1 detection result. Cropping image!")
                        await cropper.inference_and_save_image()  # crop the image
                    else:  # no detection results, so don't crop it, just save the image
                        logging.error("No detection results. Using the whole image.")
                        await image_tools.save_to_file_system(img_byte_arr, plant_image_cropped_path)

                    common_name, scientific_name = await identify_plant(plant_image_cropped_path)

                    logging.info(f"common_name {common_name}")
                    logging.info(f"scientific_name {scientific_name}")

                    if number_of_plants == 0:  # first plant
                        new_Plant = models.Plant(absolute_path=str(plant_image_cropped_path),
                                                 common_name=common_name,
                                                 scientific_name=scientific_name,
                                                 is_first=True)
                    else:
                        new_Plant = models.Plant(absolute_path=str(plant_image_cropped_path),
                                                 common_name=common_name,
                                                 scientific_name=scientific_name,
                                                 is_first=False)
                    # db.update(models.Progressbar).where(position.).values(fullname='Patrick the Star')
                    db.add(new_Plant)
                    db.commit()
                    # update progressbar

                except Exception as ex:
                    logging.error(f"Something Failed with PlantCropper: {plant_image_absolute_path}")
                    logging.info(ex)
                    continue
            else:
                await handle_text_commands(client_id, db, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def identify_plant(image: Path):
    try:
        logging.info("starting api request")
        plantApiWrapper = PlantApiWrapper(image)
        response: Response = plantApiWrapper.do_request()
        json_result: dict = plantApiWrapper.json_response(response)
        best_result = plantApiWrapper.get_result_with_max_score(json_result)
        species = best_result["species"]
        commonName: list = species["commonNames"]
        scientificName = species["scientificNameWithoutAuthor"]
        return commonName[0], scientificName  # just pick the first one
    except Exception:
        return "", ""


class ImageTools:
    """ Class that is responsible for rotation and conversion of images """

    def __init__(self, plant_image_absolute_path):
        self.path: Path = plant_image_absolute_path  # does not exist yet

    async def convert_if_necessary(self):
        logging.info("convert_if_necessary")
        # https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
        rotated_image = Image.open(self.path, mode='r')
        rotated_image = await self.needs_format_conversion(rotated_image)

        img_byte_arr = io.BytesIO()
        rotated_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr

    async def needs_format_conversion(self, rotated_image):
        if rotated_image.mode in ("RGBA", "P"):  # It's possible that images come in this format, if they
            # are sent form the storage of device. We need to convert them to prevent issues.
            logging.info("Converting RGBA so it's possible to save as JPG")
            rotated_image = rotated_image.convert("RGB")
        return rotated_image

    async def rotate_and_save_image(self, image_data) -> bool:
        try:
            im: Image = Image.open(io.BytesIO(image_data))
            im = im.rotate(180)  # App will send images rotated, we have to rotate back
            im.save(self.path)
            logging.info(f"Rotating image and save to {self.path}")
            return True
        except Exception as ex:
            logging.error(f"failed to rotate / save the image: {self.path}")
            logging.info(ex)
            return False

    async def save_image_db_and_file_system(self, image_data, db, path):
        try:
            await self.save_to_file_system(image_data, path)
            new_Plant = models.Plant(absolute_path=str(path))
            db.add(new_Plant)
            db.commit()
            return True
        except Exception as ex:
            logging.error(f"failed to save the image: {path}")
            logging.info(ex)
            return False

    async def save_to_file_system(self, image_data, path):
        im: Image = Image.open(io.BytesIO(image_data))
        im.save(path)

    async def image_as_bytes(self):
        rotated_image = Image.open(self.path, mode='r')
        img_byte_arr = io.BytesIO()
        rotated_image.save(img_byte_arr, format='JPEG')
        actual_bytes: bytes = img_byte_arr.getvalue()
        return actual_bytes


async def handle_text_commands(client_id, db, websocket):
    textData: str = await websocket.receive_text()
    logging.info(textData)
    is_app = await isMessageFromApp(client_id)
    if is_app:
        if "command=" in textData:
            command = textData[:]
            command = command.split("command=", 1)[1]
            logging.info(command)
            if "startTime" in command:  # startTime=2020-12-01T...
                if not timeAlreadySet(db):
                    await manager.broadcastText(
                        "Initialisiere Objekterkennungsmodell: YOLOv5l6 mit 76.8 Millionen Parameter")
                    await manager.send_personal_message(f"You wrote: {command}",
                                                        websocket)

                    await manager.broadcastText(command)  # Subtract time on client-side
                    await write_starttime_to_db(command, db)
                    await initialize_yolo()
                else:
                    logging.error("Time has already been set, skipping.")
            if "stopTime" in command:
                await manager.send_personal_message(f"You wrote: {command}",
                                                    websocket)
                await manager.broadcastText(command)
                splitted_without_commmand = command[:]
                splitted_without_commmand = splitted_without_commmand.split("stopTime=", 1)[1]
                logging.info(f"splitted_without_commmand: {splitted_without_commmand}")
                time = models.Time(time=splitted_without_commmand, description=TimeType.stopTime)
                db.add(time)
                db.commit()


        else:  # Normal Log
            new_log = models.Log(content=textData)
            db.add(new_log)
            db.commit()
            await manager.broadcastText(textData)
            await manager.send_personal_message(f"You wrote: {textData}", websocket)  # just for debugging
    else:
        # The only client that is not a passive receiver of data, is Pilot
        logging.info(" FATAL ERROR: Len(client_id) bigger than 9")


async def write_starttime_to_db(command, db):
    splitted_without_commmand = command[:]
    splitted_without_commmand = splitted_without_commmand.split("startTime=", 1)[1]
    time = models.Time(time=splitted_without_commmand, description=TimeType.startTime)
    db.add(time)
    db.commit()


async def initialize_yolo():
    """ The first detection with yolo is always slow, because it downloads the weights.
    So for that reason,  once start signal received, we just test one random plant so that  subsequent detection
    processses will be faster """
    try:
        root = get_test_image_directory()
        test_output = root / "cropped_potted_plant.jpg"
        test_input = root / "potted_plant.jpg"
        cropper = PlantBoxCropper(test_input, test_output)
        im = await cropper.save_and_return_cropped_image()
    except Exception as ex:
        logging.error("Exception in initialize_yolo")


async def get_num_plants_in_db(db):
    number_of_plants: int = db.query(models.Plant).count()
    return number_of_plants


@app.get("/websocketTest", response_class=HTMLResponse)
async def number_of_images(request: Request):
    html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Websocket Test</title>
</head>
<body>
<video controls width="250">

    <source src="../static/img/video/test_websocket.mp4"
            type="video/mp4">

    <source src="../static/img/video/test_websocket.webm"
            type="video/webm">

    Sorry, your browser doesn't support embedded videos.
</video>
</body>
</html>
    """
    return HTMLResponse(content=html_content, status_code=200)


def get_test_image_directory():
    """ Returns an Operating System agnostic path directory of the test_img. """
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    static = current_file_dir / "static"
    test_img_directory = static / "test_img"
    return test_img_directory
