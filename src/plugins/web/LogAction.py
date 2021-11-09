from pydantic.class_validators import validator
from modules.app.base.CallStack import CallStack
from modules.app.base.Configuration import *
from modules.app.base.Instances import *

@configuration
class LogActionConfiguration(ActionConfiguration):
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "web"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class LogAction(BaseAction):
    from plugins.web.Platform import Platform

    def __init__(self, parent: Platform, config: LogActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent

    def invoke(self, call_stack: CallStack):
        super().invoke(call_stack.with_(self))

        message = call_stack.get("payload")
        self.platform.add_log(message)