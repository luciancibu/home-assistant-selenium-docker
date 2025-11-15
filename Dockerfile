FROM alpine:3.18

RUN apk add --no-cache python3 py3-pip chromium chromium-chromedriver bash curl

RUN pip3 install --no-cache-dir flask selenium

COPY run.sh /run.sh
COPY server.py /server.py
COPY selenium_script.py /selenium_script.py

RUN chmod +x /run.sh

CMD ["/run.sh"]