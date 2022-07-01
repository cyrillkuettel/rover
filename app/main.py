from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, Depends
from typing import List
from pathlib import Path
import logging
import subprocess
from string import Template
from datetime import datetime, timedelta
from pandas import DataFrame
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
from .models import TimeType, Time
from .socket_manager import ConnectionManager
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session, Query
import torch
from pydantic import BaseSettings

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


def strfdelta(tdelta: timedelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def getStopTime(db: Session):
    """ Returns the Time difference in seconds """
    startTimeColumn: List[Time] = db.query(Time).filter_by(description=TimeType.startTime).all()
    stopTimeColumn: List[Time] = db.query(Time).filter_by(description=TimeType.stopTime).all()
    startTime = startTimeColumn[0].time
    stopTime = stopTimeColumn[0].time
    startTimeDateTime = datetime.fromtimestamp(int(startTime) / 1000.0)
    stopTimeDateTime = datetime.fromtimestamp(int(stopTime) / 1000.0)
    diffDateTime = stopTimeDateTime - startTimeDateTime
    return strfdelta(diffDateTime, '%M:%S')


@app.get("/api/yolo")
async def main(db: Session = Depends(get_db)):
    # https://github.com/ultralytics/yolov5/issues/7933
    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

    # Images
    img = 'https://www.gardenia.net/storage/app/public/guides/detail/WfJI7dBgdwFjRzS27I8jcqi4B3sirjFVksrxxJxQ.webp'  # or file, Path, PIL,
    # OpenCV, numpy, list

    # Inference
    results = model(img)
    box_pred: DataFrame = results.pandas().xyxy[0]
    best_index = box_pred['confidence'].idxmax()
    best = box_pred.loc[[best_index]]
    logging.info(best)
    results.print()


@app.get("/api/time")
async def main(db: Session = Depends(get_db)):
    stopTimeColumn: List[str] = db.query(models.Time).filter_by(description=TimeType.stopTime).all()
    if len(stopTimeColumn) > 0:
        time = stopTimeColumn[0]
    else:
        startTimeColumn: List[str] = db.query(models.Time).filter_by(description=TimeType.startTime).all()
        if len(startTimeColumn) > 0:
            time = startTimeColumn[0]
        else:
            time = "not-initialized"
        logging.info(f"fetched time = %s", time)
    return time


@app.get("/")
async def main(request: Request, db: Session = Depends(get_db)):
    logs: List[Query] = db.query(models.Log).all()
    number_of_plants: int = len(db.query(models.Plant).all())

    logging.info(f"number_of_plants = %s", number_of_plants)
    time = "0:00"
    if timeAlreadyStopped(db):  # display the stopped time if it exists
        time = getStopTime(db)

    return templates.TemplateResponse(
        "index.html", {"request": request,
                       "Log": logs,
                       "numer_of_images": number_of_plants,
                       "time": time,
                       "images_for_future": 12 - number_of_plants})  # expecting never more than 11 plant


"""
@app.get("/apk", )
async def serve_File():
    logging.info("Serving a file response")
    return FileResponse(path=APP, filename=paths.get_pilot_apk_name())
"""


@app.get("/clear", response_class=HTMLResponse)
async def delete_cache(request: Request, db: Session = Depends(get_db)):
    await clear_database(db)
    logging.info("clearing the images")
    logging.info(f"calling script {IMG_REMOVE}")
    subprocess.call(IMG_REMOVE)
    return "<h2>Cleared Cache :) </h2> <p>All Logging and images deleted from server</p>"


@app.get("/steam/injector/restart/")
async def restart():
    logging.info("triggered steam/injector/restart")
    _id = 777
    if _id in websocket_map:
        pilot: WebSocket = websocket_map.get(_id)
        await manager.send_personal_message("restart", pilot)


@app.get("/steam/injector/stop/")
async def stop():
    logging.info("triggered steam/injector/stop")
    _id = 777
    if _id in websocket_map:
        pilot: WebSocket = websocket_map.get(_id)
        try:
            await manager.send_personal_message("stop", pilot)
        except Exception:
            logging.info("failed to stop")


async def clear_database(db: Session):
    db.query(models.Plant).delete()
    db.query(models.Log).delete()
    logging.info("cleared database")


def timeAlreadySet(db: Session):
    timeColumn: int = len(db.query(models.Time).all())
    return timeColumn > 0


def timeAlreadyStopped(db: Session):
    timeColumn: int = len(db.query(models.Time).all())
    return timeColumn >= 2


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            if client_id == 777:
                websocket_map[client_id] = websocket
            if client_id == 888:  # 888 is the pre-defined client-id, which represents binary data
                number_of_plants: int = len(db.query(models.Plant).all())
                plant_image_absolute_path: Path = STATIC_IMG / f"plant{number_of_plants}.jpg"
                image_data: bytes = await websocket.receive_bytes()
                logging.info(f"Received bytes. Length = {len(image_data)}")
                im: Image = Image.open(io.BytesIO(image_data))
                im = im.rotate(180)
                try:
                    # save reference to stored image path in db
                    new_Plant = models.Plant(absolute_path=str(plant_image_absolute_path))
                    db.add(new_Plant)
                    db.commit()
                    im.save(plant_image_absolute_path)  # write to file system
                    # Now read the new file into a byte stream and broadcast that
                    # https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
                    rotated_image = Image.open(plant_image_absolute_path, mode='r')
                    if rotated_image.mode in ("RGBA", "P"):  # Saved images might be in this format
                        logging.info("Converting RGBA so it's possible to save as JPG")
                        rotated_image = rotated_image.convert("RGB")
                    img_byte_arr = io.BytesIO()
                    rotated_image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    logging.info("Saving the image")
                    await manager.broadcastBytes(img_byte_arr)  # Send the new image to all clients
                except Exception as ex:
                    logging.error(f"failed to save the image: {plant_image_absolute_path}")
                    logging.info(ex)

            else:
                textData = await websocket.receive_text()
                logging.info("received Text:" + textData)

                if len(str(client_id)) <= 9:  # It's the pilot
                    if "command=" in textData:
                        command = textData[:]
                        command = command.split("command=", 1)[1]
                        logging.info(command)
                        if "startTime" in command:  # startTime=2020-12-01T...
                            if not timeAlreadySet(db):
                                await manager.send_personal_message(f"You wrote: {command}",
                                                                    websocket)
                                await manager.broadcastText(command)  # Subtract time on client-side
                                splitted_without_commmand = command[:]
                                splitted_without_commmand = splitted_without_commmand.split("startTime=", 1)[1]
                                time = models.Time(time=splitted_without_commmand, description=TimeType.startTime)
                                db.add(time)
                                db.commit()
                            else:
                                logging.error("Time has already been set, skipping.")
                        if "species" in command:
                            logging.info(command)
                            await manager.broadcastText(command)
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
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/websocketTest", response_class=HTMLResponse)
async def delete_cache(request: Request):
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
