
from modules.base.CallStack import CallStack
from modules.base.Configuration import *
from modules.base.Instances import *
import bluetooth


@configuration
class RfcommActionConfiguration(ActionConfiguration):
    '''Rfcomm action to send a message through the rfcomm client.'''

    payload: Optional[str]
    '''If the payload is not set, it get's rendered from the passed values'''

    @validator('platform')
    def check_platform(cls, v):
        platform_name = "rfcomm_client"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class RfcommActionState(BaseState):
    '''Represents the state of the RFComm Action'''

    payload: Union[str, dict]
    '''Last payload'''


class Action(BaseAction, Debuggable):
    '''Rfcomm action to send a message through the rfcomm client.
    Use the variable {{{payload}}}.
    '''
    from plugins.rfcomm_client.Platform import Platform as RfcommPlatform

    def __init__(self, parent: RfcommPlatform, config: RfcommActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.configuration = config
        self.state = RfcommActionState()

    def invoke(self, call_stack: CallStack):
        call_stack = call_stack.with_element(self)

        if self.configuration.payload:
            self.state.payload = self.configuration.payload
            self.log_debug("Payload from configuration: " + str(self.state.payload))
        else:
            self.state.payload = str(call_stack.get("{{{payload}}}"))
            self.log_debug("Payload from configuration: " + str(self.state.payload))

        self.platform.publish(self.state.payload)

        return super().invoke(call_stack)
