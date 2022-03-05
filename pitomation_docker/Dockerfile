FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install \
    libjpeg-dev zlib1g-dev \
    libjpeg62-turbo-dev \
    libjpeg62 \
    pigpio-tools \
    build-essential \
    python3-pillow

RUN pip install colorzero gpiozero pigpio RPi.GPIO pydantic PyYAML pywebio chevron paho-mqtt pillow
    
RUN apt -y install alsa-utils
RUN apt -y install openssh-server

#ADD ssh /usr/local/bin/ssh
#RUN chmod +x /usr/local/bin/ssh && mkdir -p /root/.ssh
#ENTRYPOINT ["/usr/local/bin/ssh"]
#CMD []