FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV MODULE_NAME="app.main"
ENV VARIABLE_NAME="app"
ENV PORT="8000"
ENV BIND="0.0.0.0:8000"
