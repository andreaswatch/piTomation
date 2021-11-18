from sys import platform

from pydantic.class_validators import validator
from modules.base.Configuration import *
from modules.base.Instances import *

#@configuration
class HassEntityConfiguration(Configuration):
    '''Exposes an action or sensor to HomeAssistant.'''

    id: str
    '''Script id to export'''

    name: Optional[str]
    '''friendly name in HomeAssistant'''

    type: str
    '''HomeAssistant type''' 

    icon: Optional[str]
    '''Icon to show in HomeAssistant'''


@configuration
class HassTriggerEntityConfiguration(HassEntityConfiguration):
    '''Exposes an Action or Sensor to HomeAssistant as a trigger entity.'''

    event: str
    '''Event to listen for the State'''

    @validator('type')
    def check_type(cls, v):
        if "trigger" not in v:
            raise ValueError("wrong type: trigger, is: " + v)
        return v      


@configuration
class HassBinarySensorEntityConfiguration(HassEntityConfiguration):
    '''Exposes an action or sensor to HomeAssistant as a binary sensor entity.'''

    expose_state: str
    '''State to listen for ON/OFF'''

    state_topic: Optional[str]
    '''Where Homeassistant can get the state'''    

    @validator('type')
    def check_type(cls, v):
        if "sensor" not in v:
            raise ValueError("wrong type: sensor, is: " + v)
        return v          


@configuration
class HassActionEntityConfiguration(HassBinarySensorEntityConfiguration):
    '''Exposes an action or sensor to HomeAssistant as an action entity.'''

    on_command: Optional[list[AutomationConfiguration]]
    '''Automation to execute when HomeAssistant triggers ON'''

    off_command: Optional[list[AutomationConfiguration]]
    '''Automation to execute when HomeAssistant triggers OFF'''

    command_topic: Optional[str]
    '''Where HomeAssistant can publish the state'''

    @validator('type')
    def check_type(cls, v):
        if "switch" not in v:
            raise ValueError("wrong type: switch, is: " + v)
        return v          


@configuration
class HassPlatformConfiguration(PlatformConfiguration):
    '''Allows to export actions and sensors to HomeAssistant entities.'''

    @validator('platform')
    def __check_platform(cls, v):
        if "plugins.hass" not in v:
            raise ValueError("wrong platform: plugins.hass, is: " + v)
        return v

    connection: str
    '''(MQTT) Platform used for connection to HomeAssistant'''

    exports: list[Union[HassActionEntityConfiguration, HassBinarySensorEntityConfiguration, HassTriggerEntityConfiguration]]
    '''Scripts to export to HomeAssistant'''

    auto_discovery_topic: str = "homeassistant"
    '''HomeAssistant Autodiscovery topic "homeassistant" by default'''

    base_topic: Optional[str]
    '''Base topic for entity values "home/piTomation" by default'''

