from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, File, UploadFile, Depends
from typing import Optional, List

from pydantic import BaseModel

from pathlib import Path
import logging
import jinja2
import subprocess
from datetime import datetime
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import io
from io import BytesIO
from PIL import Image
import types
import requests
import json
from pprint import pprint
from .socket_manager import ConnectionManager
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

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

# Main Storage for all text-based Logging information
Incoming_Logs = []

# Main Storage for all plant images
Incoming_Images = []

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

    def __init__(self, initial):
        self.pilot_apk_name = "app-release.apk"
        self.plant_count = initial

    def add_pilot_apk_name(self, variable):
        self.pilot_apk_name = variable


    def get_pilot_apk_name(self):
        return self.pilot_apk_name;



manager = ConnectionManager()
paths = Paths(0)



def get_timestamp(long=False):
    if not long:
        time = datetime.now().strftime("%H:%M:%S.%f")
        return time[:-3]
    else:
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S.%f")  # dd/mm/YY H:M:S format
        return date_time[:-3]


@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    count = paths.plant_count
    logging.info("Serving TemplateResponse. with plant_count = %d  ", count)
    return templates.TemplateResponse(
        "index.html", {"request": request,
                       "Incoming_Logs": Incoming_Logs,
                       "numer_of_images": count,
                       "images_for_future": 12 - count})  # There will be a maximum of 11 plants



# Helper function to access the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# new index.html with database:
@app.get("/main")
def main(request: Request, db: Session = Depends(get_db)):
    logs = db.query(models.Log).all()
    count = paths.plant_count
    logging.info("this is the new main")
    return templates.TemplateResponse(
        "index2.html", {"request": request,
                       "Log": logs,
                       "numer_of_images": count,
                       "images_for_future": 12 - count})






@app.get("/apk", )
async def serve_File():
    logging.info("Serving a file response")
    return FileResponse(path=APP, filename=paths.get_pilot_apk_name())


@app.get("/clear", response_class=HTMLResponse)
async def delete_cache(request: Request):
    logging.info("clearing the Incoming_Logs")
    Incoming_Logs.clear()
    paths.plant_count = 0
    logging.info("clearing the images")
    logging.info(f"calling script {IMG_REMOVE}")
    subprocess.call(IMG_REMOVE)
    return "<h2>Cleared Cache :) </h2> <p>All Logging and images deleted from server</p>"




async def do_plant_api_request(image_path):

    API_KEY = "2b10rYOrxC0HDiZzccuFce"  # Set you API_KEY here
    api_endpoint = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

    image_path_1 = image_path
    image_data_1 = open(image_path_1, 'rb')

    data = {
        'organs': ['leaf']
    }

    files = [
        ('images', (image_path_1, image_data_1)),
    ]

    req = requests.Request('POST', url=api_endpoint, files=files, data=data)
    prepared = req.prepare()

    s = requests.Session()
    response = s.send(prepared)
    json_result = json.loads(response.text)
    logging.info(response.status_code)
    return json_result


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            if str(client_id) == "888":  # 888 is the pre-defined client-id, which stands for binary data
                paths.plant_count += 1
                plant_image_absolute_path = STATIC_IMG / f"plant{paths.plant_count}.jpg"

                image_data = await websocket.receive_bytes()
                im = Image.open(io.BytesIO(image_data))
                logging.info(f"Received bytes. Length = {len(image_data)} ")

                try:
                    # todo: save image to databse.
                    im.save(plant_image_absolute_path)
                    logging.info("Saving the image")
                    # response = doPostRequest(plant_image_absolute_path)
                    # logging.info(response)
                except Exception as ex:
                    # TODO: request image again maybe?
                    logging.debug(f"failed to save the image: {plant_image_absolute_path}")
                    logging.info(ex)
                await manager.broadcastBytes(image_data)  # Send the new image to all clients
            else:
                data = await websocket.receive_text()
                logging.info("received Text:" + data)

                if len(str(client_id)) <= 9:  # It's a Smartphone with The app
                    if "command=" in data:
                        command = data[:]
                        splitted_command_from_text = command.split("command=", 1)[1]
                        logging.info(splitted_command_from_text)
                        if "startTime" in splitted_command_from_text:  # startTime=2020-12-01T...
                            logging.info("sending start Signal to client. Browser should handle the rest");
                            await manager.send_personal_message(f"You wrote: {splitted_command_from_text}", websocket)
                            await manager.broadcastText(splitted_command_from_text)  # Let the client handle the rest
                        if splitted_command_from_text == "requestTime":
                            stamp = get_timestamp(long=True)
                            await manager.send_personal_message(f"time={stamp}", websocket)
                    else:  # Normal Log

                        log_entry = data
                        Incoming_Logs.append(log_entry)  # Just to store all Logs on the server side as well.
                        # This effectively reloads them from memory, the next time the page is fully reloaded.
                        # Thus, we have achieved a primitive kind of persistence
                        await manager.send_personal_message(f"You wrote: {data}", websocket)
                        await manager.broadcastText(log_entry)
                else:
                    # The only client that is not a passive receiver of data, is Pilot
                    logging.info(" FATAL ERROR: Len(client_id) bigger than 9")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
