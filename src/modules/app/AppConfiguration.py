'''
## Basic application configuration.
+ The settings files are read with pyyaml and processed by pydantic.
+ Most values are rendered with pystache which uses the mustache syntax (https://mustache.github.io/).
'''

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class AppConfiguration(VariablesConfiguration):
    """Basic application configuration.
<details>
```YAML
device:
  name: MyPiDevice
  version: 1.0

platforms:
- platform: plugins.gpio
  id: gpio
  factory: rpigpio

- platform: plugins.console
  id: console

actions:
- id: print
  platform: console
  type: PrintAction

sensors:
- id: button1
  platform: gpio
  pin: GPIO24
  type: ButtonSensor
  on_press:
  - actions:
    - action: print
      values:
        payload: Button1 pressed
```    
</details>
"""

    device: DeviceConfiguration
    """Device configuration. 
<details>
Access the device from YAML:
```
values:
 - payload: "{{id(device).configuration.name}}"
```
</details>
"""

    platforms: Optional[list[WithPlugins(PlatformConfiguration)]] #type: ignore
    """List of platforms, see `plugins`
<details>
Access a platfrom from YAML:
```
values:   
 - payload: "{{id(id_of_the_platform).variables.myVariable}}"
```
</details>
"""

    actions: Optional[list[WithPlugins(ActionConfiguration)]] #type: ignore
    """List of actions (=outputs), see `plugins`
<details>
Access an action from YAML:
```
values:   
 - payload: "{{id(id_of_the_action).variables.myVariable}}"
```
</details>
"""    

    sensors: Optional[list[WithPlugins(SensorConfiguration)]] #type: ignore
    """List of sensors (=inputs), see `plugins`
<details>
Access a sensor from YAML:
```
values:   
 - payload: "{{id(id_of_the_sensor).variables.myVariable}}"
```
</details>
"""
