FROM alpine:3.18

RUN apk add --no-cache python3 py3-pip chromium chromium-chromedriver bash curl

RUN pip3 install --no-cache-dir flask selenium

COPY server.py /server.py
COPY selenium_script.py /selenium_script.py


# Start the HTTP API service
CMD ["python3", "/server.py"]