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

    async def broadcastText(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    # This function sends the image as binary to all clients. Clients are people visiting the website currently
    # The reason I use this approach, it that the images just 'pop-up' in the browser,
    # they are automatically dynamically generated, so to speak.
    # The browser does not have to ask ever X seconds: "Is there a new image?"
    async def broadcastBytes(self, message: bytes):
        for connection in self.active_connections:
            # TODO:
            # maybe skip the Pilot client id in the list
            # It's not necessary and worse: adds unnecessary complexity
            await connection.send_bytes(message)