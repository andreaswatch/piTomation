
import time

from modules.base.Instances import *
from plugins.system.Platform import *

@configuration
class DelayActionConfiguration(ActionConfiguration):
    '''Allows to sleep for a given duration. Pass the amount of seconds in {{{payload}}}.'''

    @validator('platform')
    def check_platform(cls, v):
        platform_name = "system"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class DelayActionState(BaseState):
    '''Represents the state of the Delay Action'''

    delay_seconds: float
    '''Last programmed delay in seconds'''

    is_active: bool
    '''True if the delay is actually active'''


class DelayAction(BaseAction):
    '''Executees python's time.sleep({{{payload}}})'''

    def __init__(self, parent: Platform, config: DelayActionConfiguration) -> None:
        super().__init__(parent, config)
        self.state = DelayActionState()

    def invoke(self, call_stack: CallStack):

        seconds = float(call_stack.get("{{{payload}}}"))
        
        self.state.delay_seconds = seconds
        self.state.is_active = True
        self.on_state_changed(call_stack)

        time.sleep(seconds)

        self.state.delay_seconds = 0
        self.state.is_active = False

        super().invoke(call_stack.with_element(self))

