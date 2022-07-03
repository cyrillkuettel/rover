#!/bin/bash
# convenience script to show the Standard Output of the python container
# Note: only works in production
docker ps -aqf "name=rover_python" | xargs -I{} docker logs -f {} 
