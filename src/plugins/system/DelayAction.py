
import time

from modules.app.base.Instances import *
from plugins.system.Platform import *

@configuration
class DelayActionConfiguration(ActionConfiguration):
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "system"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class DelayAction(BaseAction):

    def __init__(self, parent: Platform, config: DelayActionConfiguration) -> None:
        super().__init__(parent, config)

    def invoke(self, call_stack: CallStack):

        message = float(call_stack.get("payload"))
        time.sleep(message)

        super().invoke(call_stack.with_(self))

