
from sys import platform

from pydantic.class_validators import validator
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class SystemPlatformConfiguration(PlatformConfiguration):

    platform: str
    
    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.system" not in v:
            raise ValueError("wrong platform: plugins.system, is: " + v)
        return v

class Platform(BasePlatform):

    def __init__(self, parent: Stackable, config: PlatformConfiguration) -> None:
        super().__init__(parent, config)



   