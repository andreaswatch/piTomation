
import time

from modules.base.Instances import *
from plugins.system.Platform import *

@configuration
class DelayActionConfiguration(ActionConfiguration):
    '''Alows to sleep for a given duration. Pass the amount of seconds in {{payload}}.'''

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "system"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class DelayAction(BaseAction):
    '''Executees python's time.sleep({{payload}})'''
    def __init__(self, parent: Platform, config: DelayActionConfiguration) -> None:
        super().__init__(parent, config)

    def invoke(self, call_stack: CallStack):

        message = float(call_stack.get("{{payload}}"))
        time.sleep(message)

        super().invoke(call_stack.with_element(self))

