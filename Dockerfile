FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# COPY ./app /code/app      (I use volume instead)

ENV MODULE_NAME="app.main"
ENV VARIABLE_NAME="app"
ENV PORT="8000"
ENV BIND="0.0.0.0:8000"
