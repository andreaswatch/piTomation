from modules.base.Instances import *
from modules.base.Configuration import *

@configuration
class UpdateActionConfiguration(ActionConfiguration):
    '''Writes a given {{payload}} into the table row {{topic}}.'''

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "web"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class UpdateActionState(BaseState):
    topic: str
    payload: str

class UpdateAction(BaseAction):
    '''Writes a given {{payload}} into the table row {{topic}}.'''

    from plugins.web.Platform import Platform

    def __init__(self, parent: Platform, config: UpdateActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.state = UpdateActionState()

    def invoke(self, call_stack: CallStack):
        self.state.topic = str(call_stack.get("{{topic}}"))
        self.state.payload = str(call_stack.get("{{payload}}"))
        
        self.platform.update(self.state.topic, self.state.payload)

        super().invoke(call_stack.with_element(self))
