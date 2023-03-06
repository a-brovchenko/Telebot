FROM python:3.8.16-alpine3.17

RUN \
    echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" > /etc/apk/repositories && \
    echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories

RUN \
    apk update && \
    apk add --no-cache chromium chromium-chromedriver

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY * ./

ENTRYPOINT [ "python", "/app/Bot.py" ]
