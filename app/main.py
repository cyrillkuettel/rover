from fastapi import FastAPI, WebSocket, Request
from typing import Optional

from pathlib import Path
import logging
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
                    )

current_file = Path(__file__)
current_file_dir = current_file.parent  # /code/app
project_root = current_file_dir.parent  # /code/
project_root_absolute = project_root.resolve()

static_root_absolute = current_file_dir / "static"
TEMPLATES = current_file_dir / "templates"
INDEX_HTML_PATH = static_root_absolute / "index.html"
CSS_PATH = static_root_absolute / "css"  # find a way to reference this variable

templates = Jinja2Templates(directory=TEMPLATES)

"""
html = ""
with open(INDEX_HTML_PATH, 'r') as f:
    html = f.read()

"""

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>    
            var ip = "192.168.188.38";
            
            var ws = new WebSocket("ws://0.0.0.0/ws");
            console.log("created Websocket endpoint");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/test/")
async def get():
    return HTMLResponse(html)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.info('Accepting client connection...')
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            data = await websocket.receive_text()
            logging.info("received Text:" + data)
            # Send message to the client
            # await websocket.send_text(f"Message text was: {data}")
        except Exception as e:
            logging.error('websocket_endpoint: error:', e)
            logging.exception("message")
            break


def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "Hello WebSocket"}
