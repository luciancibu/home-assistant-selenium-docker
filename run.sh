#!/bin/bash

# -----------------------------------------
# run.sh
# Runs Selenium reservation weekly at a specific day and time
# -----------------------------------------

MNT_DIR="/mnt/data"
SEL_DIR="$MNT_DIR/home-assistant-selenium-docker"
DOCKER_IMAGE="selenium_ha"

TARGET_DAY=2      # Tuesday
TARGET_HOUR=19    # 24h format
TARGET_MIN=53

mkdir -p "$SEL_DIR/logs"

cp -r /config/home-assistant-selenium-docker "$SEL_DIR"
chmod +x "$SEL_DIR"/*

cd "$SEL_DIR" || { echo "Failed to cd into $SEL_DIR"; exit 1; }

while true; do
    DAY=$(date +%u)
    HOUR=$(date +%H)
    MIN=$(date +%M)

    if [ "$DAY" -eq $TARGET_DAY ] && [ "$HOUR" -eq $TARGET_HOUR ] && [ "$MIN" -eq $TARGET_MIN ]; then
        for i in {1..5}; do
            docker run --rm \
                -v "$SEL_DIR/profile$i:/app/profile$i" \
                -v "$SEL_DIR/logs:/app/logs" \
                "$DOCKER_IMAGE" \
                python /app/selenium_script.py /app/profile$i /app/logs/reservation$i.txt &
        done

        wait
        sleep $((60 * 60 * 24 * 5))
    else
        sleep 60
    fi
done
