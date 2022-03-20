#/bin/bash

echo "Let's run! Starting processs: compose down, build and up --detached."
docker-compose down
git fetch origin
git pull origin main
docker-compose build
docker-compose up --build --detach
