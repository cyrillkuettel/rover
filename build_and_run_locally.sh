#!/bin/bash

docker stop $(docker ps -a -q)
docker rm $(docker ps --filter status=exited -q)
docker build -t myimage -f Dockerfile-localBuild .
docker run -d --name mycontainer -p 8000:8000 -e MODULE_NAME="app.main" -e VARIABLE_NAME="app" -v /home/cyrill/rover/app:/code/app myimage /start-reload.sh | xargs -I{} docker logs -f {} 
