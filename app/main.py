from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from typing import Optional, List
from pathlib import Path
import logging
import jinja2
from datetime import datetime
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

# Main Storage for all text-based information from the rover
Incoming_Logs = []


# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s', )


html2 = """
<!DOCTYPE html>
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <meta name="description" content=""/>
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="static/css/main.css">
        
    <title>Rover</title>    
</head>

<header>
    <div class="w3-container">
        <h1><a href="index.html"></a>Gruppe 38</h1>
     
    </div>
</header>

<div class="w3-container timer">
    <div id="numbers">
        <span id="hours">00:</span>
        <span id="mins">00:</span>
        <span id="seconds">00</span>
    </div>
</div>

<div class="w3-container">
    <div class="w3-container">
        <h2>Real-time logs</h2>
    </div>

    <ul class="w3-ul w3-card-4 w3-margin-bottom w3-margin-top w3-padding-16 " id="messages">
     </ul>
        <script>
            var client_id = Date.now()
        
            var ws = new WebSocket(`ws://localhost:80/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
        </script>
   

    <!-- w3.CSS buffering Symbol -->
    <!-- <p><i class="fa fa-spinner w3-spin" style="font-size:64px"></i></p> -->


    <div class="flex_container_main_Pot">
        <div class="w3-container w3-card-4">
            <img src="../static/img/minze-im-topf.jpg" alt="Pfefferminze" class="w3-image flex_container_main_Pot"
                 id="detected-image">
        </div>
        <div class="w3-container w3-card-4">
            <h2> Pfefferminze</h2> <!-- Hier ein Symbol bild einfügen, -->
        </div>
    </div>


    <div class="w3-container">
        <p>Reihen-Position: </p>
    </div>


    <div class="flex_container_pots">
        <div class="w3-container">
            <img class="w3-image" src="../static/img/plant-icons/plant1.png" alt="">
        </div>
        <div class="w3-container">
            <img class="w3-image" src="../static/img/plant-icons/plant2.png" alt="">
        </div>
        <div class="w3-container">
            <img class="w3-image" src="../static/img/plant-icons/plant3.png" alt="">
        </div>
        <div class="w3-container">
            <img class="w3-image" src="../static/img/plant-icons/plant4.png" alt="">
        </div>
        <div class="w3-container">
            <img class="w3-image" src="../static/img/plant-icons/plant5.png" alt="">
        </div>
    </div>

    <br>


    <div class="flex_container_arrow">
        <div class="w3-container">
            <img class="w3-image" src="../static/img/arrow_transparent.png" alt="">
        </div>
    </div>


</div>
</body>

<footer>
    <div class="footer-container">
        <div class="footer-center">
            <p> HSLU HS2021 - PREN 1 & 2 Gruppe 38 Copyright &copy;</p>
        </div>
    </div>
</footer>
</html>
"""


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
    return HTMLResponse(html2)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            #  Here we can create if statements for the type of socket connection and what kind of information in will
            # convey.
            data = await websocket.receive_text()
            Incoming_Logs.append(data) # Just to store all Logs on the server side as well
            logging.info("received Text:" + data)
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            stamp = get_timestamp()
            await manager.broadcast(f"{stamp}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
