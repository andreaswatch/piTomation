Please note that this is an early Alpha Version.

# piTomation

piTomation is a system to control your Raspberry Pi and similar devices by simple yet powerful configuration files and control them remotely.
API description: https://andreaswatch.github.io/piTomation/

# Concept

This service is fully configurable through YAML files. It's recommended to read the sample configuration in src/raspberrypi.yaml.
The YAML allows to configure platforms that provide a given functionality, sensors to read values from the platform and actions to send values to the platform.
As an example, the GPIO platform provides access to GPIO pins. The GpioButtonSensor can read a button state and the GpioAction can set the pin state (e.g. LOW/HIGH).

## Config file
piTomation needs to have a valid yaml config file. As an example, frontdoor.yaml can be used.
By default, piTomation tries to find the config file by the actual hostname. However, it is possible to pass a filename as commandline argument.

# Install & Run

There are several methods to run piTomation.
The easiest is to run it in docker.

---

Option 1) Docker
```
cd ~
git clone --recurse-submodules http://github.com/andreasWatch/piTomation
cd piTomation/src
cp frontdoor.yaml ~/frontdoor.yaml #create your custom config file..
cd pitomation_docker
./build_container.sh 
./run_container.sh
```

---

Option 2) Debian Bullseye
Debian Bullseye comes with Python 3.9
```
cd ~
git clone --recurse-submodules http://github.com/andreasWatch/piTomation
sudo apt-get update && apt-get -y install \
    libjpeg-dev zlib1g-dev \
    libjpeg62-turbo-dev \
    libjpeg62 \
    pigpio-tools \
    build-essential \
    python3-pillow
pip install colorzero gpiozero pigpio RPi.GPIO pydantic PyYAML pywebio chevron paho-mqtt pillow
copy piTomation/frontdoor.yaml ~/frontdoor.yaml #create your custom config file..
python piTomation
```

---

Option 3) Debian Buster
RaspberryPi OS delivers Python 3.7, but piTomation is based on Python 3.9.

Install Python 3.9
```
wget -qO - https://raw.githubusercontent.com/tvdsluijs/sh-python-installer/main/python.sh | sudo bash -s 3.9.7
```
(From: https://itheo.tech/ultimate-python-installation-on-a-raspberry-pi-ubuntu-script/ )

### Ensure python version 
```
python --version
# Python 3.9.7
```

### install pip
```
python -m ensurepip --upgrade
```

Now, follow the steps of Option 2 - Debian Buster.


# Docs

https://andreaswatch.github.io/piTomation

**Build the docs:**
```
pip3 install pdoc #need to install pdoc
cd ~/piTomation/docs
rm -f *.html
cd ~/piTomation/src
pdoc --html . --force --output-dir ../docs
```
