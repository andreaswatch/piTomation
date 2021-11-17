
from sys import platform

from pydantic.class_validators import validator
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class SystemPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the System platform.'''
    
    @validator('platform')
    def __check_platform(cls, v):
        if "plugins.system" not in v:
            raise ValueError("wrong platform: plugins.system, is: " + v)
        return v

class Platform(BasePlatform):
    '''System platform'''

    def __init__(self, parent: Stackable, config: PlatformConfiguration) -> None:
        super().__init__(parent, config)



   