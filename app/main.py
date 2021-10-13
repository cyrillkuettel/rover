from fastapi import FastAPI, WebSocket, Request
from typing import Optional

from pathlib import Path
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Websockets are going to be a dependency
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
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


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )



