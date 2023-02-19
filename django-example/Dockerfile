FROM python:3.8-slim

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt-get -y install libpq-dev gcc \
    && pip install psycopg2


RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

RUN chmod +x entrypoint.sh