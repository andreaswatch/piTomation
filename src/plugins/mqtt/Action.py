
from modules.base.CallStack import CallStack
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class MqttActionConfiguration(ActionConfiguration):
    '''Mqtt action to send a message through the mqtt client.'''

    topic: Optional[str]
    '''If the topic is not set, it get's rendered from the passed values'''

    payload: Optional[Union[str, dict]]
    '''If the payload is not set, it get's rendered from the passed values'''

    retain: Optional[bool]
    '''If retain is not set, it get's rendered from the passed values'''

    @validator('platform')
    def check_platform(cls, v):
        platform_name = "mqtt"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class MqttActionState(BaseState):
    '''Represents the state of the MQTT Action'''

    topic: str
    '''Last topic'''

    payload: Union[str, dict]
    '''Last payload'''

    retain: Optional[bool]
    '''Returns true, if the last message was retained'''


class Action(BaseAction, Debuggable):
    '''Mqtt action to send a message through the mqtt client.
    Use the variables {{topic}}, {{{payload}}} and optionally {{retain}}.
    '''
    from plugins.mqtt.Platform import Platform as MqttPlatform

    def __init__(self, parent: MqttPlatform, config: MqttActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.configuration = config
        self.state = MqttActionState()

    def invoke(self, call_stack: CallStack):
        call_stack = call_stack.with_element(self)

        if self.configuration.topic:
            self.state.topic = self.configuration.topic
            self.log_debug("Topic from configuration: " + self.state.topic)
        else:
            self.state.topic = str(call_stack.get("{{topic}}"))
            self.log_debug("Topic from values: " + self.state.topic)
        
        if self.configuration.payload:
            self.state.payload = self.configuration.payload
            self.log_debug("Payload from configuration: " + str(self.state.payload))
        else:
            self.state.payload = str(call_stack.get("{{{payload}}}"))
            self.log_debug("Payload from configuration: " + str(self.state.payload))

        if hasattr(self.configuration, 'retain'):
            self.state.retain = self.configuration.retain
            self.log_debug("Retain from configuration: " + str(self.state.retain))
        else:
            retain = call_stack.get("{{retain}}", optional=True)
            if retain == "1" or retain == "True" or retain == "true":
                self.state.retain = True
            if retain is None:
                self.state.retain = False
            self.log_debug("Retain from configuration: " + str(self.state.retain))

        self.platform.publish(self.state.topic, self.state.payload, retain = (self.state.retain == True))

        return super().invoke(call_stack)
