from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, Depends
from typing import List
from pathlib import Path
import logging
import subprocess
from datetime import datetime
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import io
import os
from PIL import Image
from .socket_manager import ConnectionManager
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session, Query

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
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

websocket_map = {}  # This is useed to get websocket object by id


def get_timestamp(long=False):
    if not long:
        time = datetime.now().strftime("%H:%M:%S.%f")
        return time[:-3]
    else:
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S.%f")  # dd/mm/YY H:M:S format
        return date_time[:-3]


# Helper function to access the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/time")
async def main(db: Session = Depends(get_db)):
    timeColumn: List[str] = db.query(models.Time).all()
    if len(timeColumn) > 0:
        time = timeColumn[0]
    else:
        time = "not-initialized"
    logging.info(f"fetched time = %s", time)
    logging.info(f"fetched time = %s", time)
    return time


@app.get("/")
async def main(request: Request, db: Session = Depends(get_db)):
    logs: List[Query] = db.query(models.Log).all()
    number_of_plants: int = len(db.query(models.Plant).all())

    logging.info(f"number_of_plants = %s", number_of_plants)

    return templates.TemplateResponse(
        "index.html", {"request": request,
                       "Log": logs,
                       "numer_of_images": number_of_plants,
                       "images_for_future": 12 - number_of_plants})  # expecting never more than 11 plant


@app.get("/apk", )
async def serve_File():
    logging.info("Serving a file response")
    return FileResponse(path=APP, filename=paths.get_pilot_apk_name())


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


async def clear_database(db: Session):
    db.query(models.Plant).delete()
    db.query(models.Log).delete()
    logging.info("cleared database")


def timeAlreadySet(db: Session):
    timeColumn: int = len(db.query(models.Time).all())
    return timeColumn > 0


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
                image_data = await websocket.receive_bytes()
                im = Image.open(io.BytesIO(image_data))
                im.rotate(180)
                logging.info(f"Received bytes. Length = {len(image_data)}")
                try:
                    im.save(plant_image_absolute_path)  # write to file system
                    # save reference to stored image path in db
                    new_Plant = models.Plant(absolute_path=str(plant_image_absolute_path))
                    db.add(new_Plant)
                    db.commit()
                    logging.info(f"file size on disk: {os.stat('somefile.ext').st_size}")
                    logging.info("Saving the image")
                except Exception as ex:
                    logging.debug(f"failed to save the image: {plant_image_absolute_path}")
                    logging.info(ex)
                await manager.broadcastBytes(image_data)  # Send the new image to all clients
            else:
                textData = await websocket.receive_text()
                logging.info("received Text:" + textData)

                if len(str(client_id)) <= 9:  # It's the pilot
                    if "command=" in textData:
                        command = textData[:]
                        splitted_command_from_text = command.split("command=", 1)[1]
                        logging.info(splitted_command_from_text)
                        if "startTime" in splitted_command_from_text:  # startTime=2020-12-01T...
                            if not timeAlreadySet(db):
                                logging.info("sending start Signal to client. The client's browser should handle the "
                                             "rest")
                                await manager.send_personal_message(f"You wrote: {splitted_command_from_text}", websocket)
                                await manager.broadcastText(splitted_command_from_text)  # Subtract time on client-side
                                time = models.Time(time=splitted_command_from_text)
                                db.add(time)
                                db.commit()
                            else:
                                logging.error("Time has already been set, skipping.")
                        if splitted_command_from_text == "requestTime":
                            stamp = get_timestamp(long=True)
                            await manager.send_personal_message(f"time={stamp}", websocket)
                        if "species" in splitted_command_from_text:
                            logging.info(splitted_command_from_text)
                            await manager.broadcastText(splitted_command_from_text)

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
