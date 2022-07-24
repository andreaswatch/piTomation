FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install \
    openssh-server \
    libjpeg-dev zlib1g-dev \
    libjpeg62-turbo-dev \
    libjpeg62 \
    alsa-utils \
    pigpio-tools \
    build-essential \
    python3-pillow \
    python3-bluez \
    curl

RUN pip install colorzero gpiozero pigpio RPi.GPIO \
    pydantic PyYAML pywebio chevron paho-mqtt pillow
    