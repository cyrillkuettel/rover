from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from typing import Optional, List
from pathlib import Path
import logging
import jinja2
from datetime import datetime
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

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

# Main Storage for all text-based information from the rover
Incoming_Logs = []

current_file = Path(__file__)
current_file_dir = current_file.parent  # /code/app
TEMPLATES = current_file_dir / "templates"
FILES = current_file_dir / "files"
APP = FILES / "pilot.apk"
static = current_file_dir / "static"
STATIC_IMG = static / "img"
FAVICON = STATIC_IMG / "favicon.ico"
templates = Jinja2Templates(directory=TEMPLATES)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s', )


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


def get_timestamp():
    time = datetime.now().strftime("%H:%M:%S.%f")
    return time[:-3]


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "Incoming_Logs": Incoming_Logs})


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(FAVICON)


@app.get("/apk/", )
async def serve_File():
    logging.info("Serving a file response")
    return FileResponse(path=APP, filename="pilot.apk")


@app.get("/deleteCache/", response_class=HTMLResponse)
async def del_cache(request: Request):
    logging.info("clearing the Incoming_Logs")
    Incoming_Logs.clear()
    return "<h2>Cleared Cache :)</h2>"


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            #  Here we can create if statements for the type of socket connection and what kind of information it will
            # convey.
            stamp = get_timestamp()
            data = await websocket.receive_text()
            Incoming_Logs.append(f"{stamp}: {data}")  # Just to store all Logs on the server side as well.
            # This effectively reloads them from memory, the next time the page is fully reloaded.
            # Thus, we have achieved a "primitive persistence functionality"
            logging.info("received Text:" + data)
            await manager.send_personal_message(f"You wrote: {data}", websocket)  # this is not really necessary
            await manager.broadcast(f"{stamp}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
