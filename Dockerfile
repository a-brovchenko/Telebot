FROM python:3.8.16-alpine3.17

WORKDIR /app
COPY * ./
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python", "/app/Telebot.py" ]
