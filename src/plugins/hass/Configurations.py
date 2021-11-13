from sys import platform

from pydantic.class_validators import validator
from modules.app.base.Configuration import *
from modules.app.base.Instances import *

@configuration
class HassEntityConfiguration(BaseModel):
    id: str
    '''script id to export'''

    name: Optional[str]
    '''friendly name in Homeassistant'''

    type: str
    '''Homeassistant type''' 


@configuration
class HassTriggerEntityConfiguration(HassEntityConfiguration):
    event: str
    '''event to listen for the state'''

    @validator('type')
    def check_platform_module(cls, v):
        if "trigger" not in v:
            raise ValueError("wrong type: trigger, is: " + v)
        return v      


@configuration
class HassBinarySensorEntityConfiguration(HassEntityConfiguration):
    on_event: str
    '''event to listen for ON'''

    off_event: str    
    '''event to listen for OFF'''

    state_topic: Optional[str]
    '''where Homeassistant can get the state'''    

    @validator('type')
    def check_platform_module(cls, v):
        if "sensor" not in v:
            raise ValueError("wrong type: sensor, is: " + v)
        return v          


@configuration
class HassActionEntityConfiguration(HassBinarySensorEntityConfiguration):

    on_command: str     
    '''command to execute when Homeassistant triggers ON'''

    off_command: str   
    '''command to execute when Homeassistant triggers OFF'''

    command_topic: Optional[str]
    '''where Homeassistant can publish the state'''

    @validator('type')
    def check_platform_module(cls, v):
        if "action" not in v:
            raise ValueError("wrong type: action, is: " + v)
        return v          


@configuration
class HassPlatformConfiguration(PlatformConfiguration):

    platform: str

    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.hass" not in v:
            raise ValueError("wrong platform: plugins.hass, is: " + v)
        return v

    '''(mqtt) platform used for connection to hass'''
    connection: str

    '''scripts to display in the dashboard'''
    exports: list[Union[HassActionEntityConfiguration, HassBinarySensorEntityConfiguration, HassTriggerEntityConfiguration]]

    '''Homeassistant Autodiscovery topic "homeassistant" by default'''
    auto_discovery_topic: str = "homeassistant"

    '''Base topic for entity values "home/piTomation" by default'''
    base_topic: str = "home/piTomation"

