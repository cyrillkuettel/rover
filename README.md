# Rover Front- and Backend
It's a Web-App to display dynamic status information, there is a continuous steram of incoming updates. To have the images and text dynamically appear, websockets are being used. WebSockets allow for a higher amount of efficiency compared to REST because they do not require the HTTP request/response overhead for each message sent and received.

# Features and Credits 

* Using [a 73 Million parameter object detection model](https://github.com/ultralytics/yolov5#pretrained-checkpoints) to detect potted plant from incoming image and cut out one bounding box. 

* Implemented asynchronous api calls to the [Pl@ntNet identify API](https://identify.plantnet.org/) to determine plant species. 
* It uses [FastAPI](https://fastapi.tiangolo.com/) framework for API development. FastAPI is a modern, highly performant, web framework for building APIs with Python.

* The APIs are served with [Gunicorn](https://gunicorn.org/) server with multiple [Uvicorn](https://www.uvicorn.org/) workers. Uvicorn is a lightning-fast "ASGI" server. Univorn runs asynchronous Python web code in a single process.

* Reverse-proxying with [Nginx](https://www.nginx.com). Nginx is very good at serving static content. 

* Dockerized using the [uvicorn-gunicorn-fastapi-docker](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker) Docker image.


# System Architecture Overview
![](https://github.com/cyrillkuettel/rover/blob/main/doc/diagram/w.png)
The System consists of two docker containers: Gunicorn and Nginx. How can they communicate? Well, they use a shared volume, it's that simple. Most requests are not served by nginx directly, but passed back to the Gunicorn / FastAPI app which sits behind nginx. These are dynamic calls, rather than static content. This can be implemented by setting a proxy_pass in the nginx.conf.

## Worker Threads
The number of Worker threads is variable. Generally speaking, they scale with the number of CPU cores. This configuration can be overridden in the [varia/gunicorn.conf](gunicorn.conf) file. 

# Milestones
- [x] Websocket endpoint for low-latency bidirectional coummunication
- [x] Dynamically display status information
- [X] Display pictures, updated by ![App](https://github.com/cyrillkuettel/ecstatic-pilot)
- [x] Timer, fetch Timestamp from device
- [X] Switch between tabs
- [x] nginx running in docker
- [x] Specify species and similarity of plants.
- [x] species -> API
- [x] Show Progress bar
- [ ] image processing: image comparision algorithm

# Start Local dev Environment: Linux
## API Key
The app expects a constants.py in the `app` directory. This class contains the api-key which is needed for plant identification.
Get a key for [plantnet](https://my.plantnet.org/usage).
Create a file constants.py which contains a class `Constants` and replace the `<your-api-key>` with the api key you got from plantnet.
```python
class Constants:
    def __init__(self):
        self.api_key = "<your-api-key>"

```
After that, startup quickly with Docker:
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
# Deploying
## SSL
This application expects a valid certificate at `~/cert/rover`. You can edit this path in the `docker-compose` file. To get a certificate, I followed this [https://help.zerossl.com/hc/en-us/articles/360058295894-Installing-SSL-Certificate-on-NGINX](tutorial). 
The certificate itself is is mounted as a volume in the nginx container. 
If you don't want SSL, you'd need to make some adjustments in the [nginx/nginx.conf](nginx.conf) file. 


