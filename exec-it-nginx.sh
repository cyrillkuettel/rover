#/bin/bash

# get the ID Of the container which runs gunicorn
echo "Getting ID"
ID=$(docker ps -aqf "ancestor=nginx")
echo "exec into /var/www/public"

docker exec -it -w /var/www/public $ID bash
