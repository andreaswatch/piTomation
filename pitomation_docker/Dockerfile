FROM python:3.9-slim-bullseye
RUN apt-get update && apt-get -y install \
    libjpeg-dev zlib1g-dev \
    libjpeg62-turbo-dev \
    libjpeg62 \
    pigpio-tools \
    build-essential \
    python3-pillow 
#pigpio
RUN pip install colorzero gpiozero pigpio RPi.GPIO pydantic PyYAML pywebio chevron paho-mqtt pillow
#alsa:
RUN apt-get -y install alsa-utils

