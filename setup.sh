#!/bin/bash

CONTAINER="hassio_supervisor"
SRC="$(pwd)"
DEST="/data/addons/local/local_selenium_reservation"

FILES=(
  "Dockerfile"
  "README.md"
  "config.json"
  "selenium_script.py"
  "server.py"
)

if [[ "$1" == "" ]]; then
    echo "===== Creating destination folder in container ====="
    docker exec "$CONTAINER" mkdir -p "$DEST"
    echo

    echo "===== Copying files to $CONTAINER:$DEST ====="
    for f in "${FILES[@]}"; do
        if [[ -f "$f" ]]; then
            echo "Copying $f :)"
            docker cp "$f" "$CONTAINER":"$DEST"/
        else
            echo "===== WARNING!!!!: File '$f' not found in $SRC"
        fi
    done
    echo "===== Copy complete ====="
    echo

    echo "===== Setting permissions on $DEST ====="
    docker exec "$CONTAINER" chmod -R 755 "$DEST"
    echo ""===== Permissions successfully applied "====="
    echo

    echo "===== ADDS-ON RELOADING ====="
    ha addons reload
    echo "===== RELOADING DONE ====="
    echo

    echo "===== RESTARTING SUPERVISOR ===="
    ha supervisor restart
    echo "===== WAIT FOR SUPERVISOR TO RESTART ===="
    sleep 10
    echo "===== DONE ====="


elif [[ "$1" == "remove" ]]; then
    echo "===== REMOVE OLD FILES ===="
    ha addons stop local_selenium_reservation 2>/dev/null
    ha addons stop local_local_selenium_reservation 2>/dev/null
    ha addons stop selenium_reservation 2>/dev/null
    ha addons uninstall local_selenium_reservation 2>/dev/null
    ha addons uninstall local_local_selenium_reservation 2>/dev/null
    ha addons uninstall selenium_reservation 2>/dev/null
    docker exec -it hassio_supervisor rm -rf /data/addons/local/local_selenium_reservation
    docker exec -it hassio_supervisor rm -rf /data/addons/local/local_local_selenium_reservation
    docker exec -it hassio_supervisor rm -rf /data/addons/local/selenium_reservation
    ha supervisor restart
    sleep 10
    echo "===== REMOVE DONE ====="
fi