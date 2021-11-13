#!/bin/bash
docker stop $(docker ps -a -q)
docker rm $(docker ps --filter status=exited -q)
docker run -d --name mycontainer -p 80:80 -e MODULE_NAME="app.main" -e VARIABLE_NAME="app" -v /home/cyrill/rover/app:/code/app myimage /start-reload.sh
