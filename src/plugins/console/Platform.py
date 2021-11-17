from pydantic.class_validators import validator
from modules.base.Configuration import *
from modules.base.Instances import *


@configuration
class ConsolePlatformConfiguration(PlatformConfiguration):
    '''Allows to output text to the Console, no configuration needed'''

    @validator('platform')
    def __check_platform(cls, v):
        if "plugins.console" not in v:
            raise ValueError("wrong platform: plugins.console, is: " + v)
        return v

class Platform(BasePlatform):
    '''Console Platform'''

    def __init__(self, parent: Stackable, config: ConsolePlatformConfiguration) -> None:
        super().__init__(parent, config)


    def dispose(self):
        return super().dispose()

   