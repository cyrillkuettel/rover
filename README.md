# Rover Front-and Backend
It's a Website to display status information, which continuously receives updates. To have the images and text dynamically appear, websockets are being used. 


# Features
* It uses [FastAPI](https://fastapi.tiangolo.com/) framework for API development. FastAPI is a modern, highly performant, web framework for building APIs with Python.

* The APIs are served with [Gunicorn](https://gunicorn.org/) server with multiple [Uvicorn](https://www.uvicorn.org/) workers. Uvicorn is a lightning-fast "ASGI" server. Univorn runs asynchronous Python web code in a single process.

* Reverse-proxying with [Nginx](https:www.nginx.com). Nginx is very good at serving static content. 

* Dockerized using the [uvicorn-gunicorn-fastapi-docker](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker) Docker image.

# System architecture overview
![](https://github.com/cyrillkuettel/rover/blob/main/doc/diagram/w.png)

The number of Worker threads is variable. Generally speaking, it can scale with the number of CPU cores.

# Milestones
- [x] Websocket endpoint for low-latency bidirectional coummunication
- [x] Dynamically display status information
- [X] Display pictures, updated by ![App](https://github.com/cyrillkuettel/ecstatic-pilot)
- [x] Timer, fetch Timestamp from device
- [X] Switch between tabs
- [x] nginx running in docker
- [ ] Specify species and similarity of plants.
- [ ] species -> API
- [ ] Show Error messages, color code it
- [ ] image processing: image comparision algorithm
- [ ] Show Progress bar

# Start Local dev Environment: Linux
Quick startup with Docker:
Open the `build_and_run_locally.sh` file.
Adjust the absolute path, it should point to the directory where you cloned the repository.
 ```bash
 ./build_and_run_locally.sh
```

# Configure Autocomplete
If you develop in a IDE, it's much easier with autocompletion.
Create a virtual environment. This will create a python interpreter for your local development environment. 

```bash
   conda create --name rover python=3.9.0
   conda activate rover
   pip install -r requirements-conda-for-local.txt 
```




### various Notes on Unvicorn
Remember to exclude the --reload uvicorn option in production. The --reload option consumes much more resources, is more unstable, etc
Try to read the gunicorn.conf file in docker container. 


