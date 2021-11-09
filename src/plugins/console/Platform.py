from pydantic.class_validators import validator
from modules.app.base.Configuration import *
from modules.app.base.Instances import *


@configuration
class ConsolePlatformConfiguration(PlatformConfiguration):

    platform: str

    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.console" not in v:
            raise ValueError("wrong platform: plugins.console, is: " + v)
        return v

class Platform(BasePlatform):
    '''Console Platform'''

    def __init__(self, parent: Stackable, config: ConsolePlatformConfiguration) -> None:
        super().__init__(parent, config)


    def dispose(self):
        return super().dispose()

   