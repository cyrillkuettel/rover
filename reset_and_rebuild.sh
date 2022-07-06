#/bin/bash

echo "Let's run! Starting processs: compose down, build and up --detached."
docker-compose down
git fetch origin
git reset --hard origin/main
rm -f ~/rover/app/test.db # very important clear the database to have a clean start
docker-compose build
docker-compose up --build --detach
