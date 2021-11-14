# piTomation

piTomation is a system to control your Raspberry Pi and similar devices by simple yet powerful configuration files and control them remotely.
https://andreaswatch.github.io/piTomation/

# Conceps

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

## piTomation
```

cd ~
git clone http://github.com/andreasWatch/piTomation
pip3 install -r piTomation/src/requirements.txt
```

## Run
```
cd ~
python3 piTomation
```

# Examples

## Example 1
Prints 'hello' to the console when the mqtt plugin connects.

```
device: 
  name: myPi
  version: "1.1"

platforms:
  - platform: plugins.mqtt
    id: mqtt
    host: home
    port: 1883
    on_connected: 
      - actions:
        - action: print
          values:
            payload: hello 

actions:
  - id: print
    platform: console
    type: PrintAction            
```

## Example 2
The sensor 'mySensor1' on the platform 'mqtt' listens to the topic 'home/abc'.
There are two automations configured, the first with conditions, the second without.
The second automation is always executed, while the first one channels if the condition is false
```
device: 
  name: myPi
  version: "1.1"

platforms:
  - platform: plugins.mqtt
    id: mqtt
    host: home
    port: 1883

actions:
  - id: print
    platform: console
    type: PrintAction            

sensors:
  - id: mySensor1
    platform: mqtt
    topic: home/abc
    on_message:
      - conditions:
          - actual: "{{id(mqtt).is_connected}}"
            comperator: equals
            expected: True
        actions:
        - action: print
          values:
            payload: "I got a message and {{id(mqtt).is_connected}} == true"      

      - actions:
        - action: print
          values:
            payload: "Got message on topic '{{topic}}', with payload '{{payload}}'"
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
