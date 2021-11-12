# piTomation

piTomation is a system to control your Raspberry Pi and similar devices by simple yet powerful configuration files and control them remotely.
https://andreaswatch.github.io/piTomation/

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
