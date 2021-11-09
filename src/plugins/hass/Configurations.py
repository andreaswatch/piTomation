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


@configuration
class HassTriggerEntityConfiguration(HassEntityConfiguration):
    event: str
    '''event to listen for the state'''


@configuration
class HassBinarySensorEntityConfiguration(HassEntityConfiguration):
    on_event: str
    '''event to listen for ON'''

    off_event: str    
    '''event to listen for OFF'''

    state_topic: Optional[str]
    '''where Homeassistant can get the state'''    


@configuration
class HassActionEntityConfiguration(HassBinarySensorEntityConfiguration):

    on_command: str     
    '''command to execute when Homeassistant triggers ON'''

    off_command: str   
    '''command to execute when Homeassistant triggers OFF'''

    command_topic: Optional[str]
    '''where Homeassistant can publish the state'''


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

