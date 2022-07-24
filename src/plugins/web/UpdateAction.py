from modules.base.Instances import *
from modules.base.Configuration import *

@configuration
class UpdateActionConfiguration(ActionConfiguration):
    '''Configuration settings for the Update Action'''

    @validator('platform')
    def check_platform(cls, v):
        platform_name = "web"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class UpdateActionState(BaseState):
    '''Represents the state of the Update Action'''

    topic: str = ""
    '''Last updated topic'''

    payload: str = ""
    '''Last payload'''


class UpdateAction(BaseAction):
    '''Write a given {{{payload}}} into the table row {{topic}}.'''

    from plugins.web.Platform import Platform

    def __init__(self, parent: Platform, config: UpdateActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.state = UpdateActionState()

    def invoke(self, call_stack: CallStack):
        self.state.topic = str(call_stack.get("{{topic}}"))
        self.state.payload = str(call_stack.get("{{{payload}}}"))
        
        self.platform.update(self.state.topic, self.state.payload)

        super().invoke(call_stack.with_element(self))
