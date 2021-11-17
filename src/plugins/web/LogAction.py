from pydantic.class_validators import validator
from modules.base.CallStack import CallStack
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class LogActionConfiguration(ActionConfiguration):
    '''Log a message to the web app. Pass the text in {{payload}}.'''

    @validator('platform')
    def __check_platform(cls, v):
        platform_name = "web"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class LogActionState(BaseState):
    '''Represents the state of the Log Action'''

    message: str
    '''Last logged message'''


class LogAction(BaseAction):
    '''Add a message from {{payload}} to the dashboard'''

    from plugins.web.Platform import Platform

    def __init__(self, parent: Platform, config: LogActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.state = LogActionState()

    def invoke(self, call_stack: CallStack):
        
        if self.configuration.variables is not None:
            call_stack.with_keys(self.configuration.variables)       

        message = call_stack.get("{{payload}}")
        self.state.message = str(message)
        
        self.platform.add_log(message)

        super().invoke(call_stack)
