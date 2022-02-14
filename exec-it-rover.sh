#/bin/bash

# get the ID Of the container which runs gunicorn
echo "Getting ID"
ID=$(docker ps -aqf "ancestor=rover_python")
echo "exec into templates"

docker exec -it -w /code/app/templates $ID bash
