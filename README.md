## Caution: Early Alpha Version

# piTomation

piTomation is a system to control your Raspberry Pi and similar devices by simple yet powerful configuration files and control them remotely.
https://andreaswatch.github.io/piTomation/

# Concept

This service is fully configurable through YAML files. It's recommended to read the sample configuration in src/raspberrypi.yaml.
The YAML allows to configure platforms that provide a given functionality, sensors to read values from the platform and actions to send values to the platform.
As an example, the GPIO platform provides access to GPIO pins. The GpioButtonSensor can read a button state and the GpioAction can set the pin state (e.g. LOW/HIGH).


# Installation
## Python 3.9
RaspberryPi OS delivers Python 3.7, but piTomation is based on Python 3.9.

### Manual method

Here is a simple instruction to install Python 3.9:
https://itheo.tech/install-python-3-9-on-raspberry-pi/

### Script
```
wget -qO - https://raw.githubusercontent.com/tvdsluijs/sh-python-installer/main/python.sh | sudo bash -s 3.9.7
```
Source: https://itheo.tech/ultimate-python-installation-on-a-raspberry-pi-ubuntu-script/

### Ensure python version 
```
python --version
# Python 3.9.7
```

### install pip
```
python -m ensurepip --upgrade
```


## piTomation
```
cd ~
git clone --recurse-submodules http://github.com/andreasWatch/piTomation
pip3.9 install -r piTomation/src/requirements.txt
```

## Run
piTomation needs to have a valid yaml config file. As an example, raspberrypi.yaml can be used.
By default, piTomation tries to find the config file by the actual hostname. However, it is possible to pass a filename as commandline argument.
```
cd ~
python piTomation
# or: python piTomation myConfigFile.yaml
```


# Docs
**Read the docs:**

https://andreaswatch.github.io/piTomation

**Building the docs:**
```
#pip3 install pdoc #need to install pdoc
cd ~/piTomation/docs
rm -f *.html
cd ~/piTomation/src
pdoc --html . --force --output-dir ../docs
```
