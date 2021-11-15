
from modules.base.CallStack import CallStack
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class MqttActionConfiguration(ActionConfiguration):
    '''Mqtt action to send a message through the mqtt client.'''
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "mqtt"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class MqttActionState(BaseState):
    topic: str
    payload: str
    retain: bool

class Action(BaseAction):
    '''Mqtt action to send a message through the mqtt client.'''
    from plugins.mqtt.Platform import Platform as MqttPlatform

    def __init__(self, parent: MqttPlatform, config: MqttActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.state = MqttActionState()

    def invoke(self, call_stack: CallStack):
        call_stack = call_stack.with_element(self)

        self.state.topic = str(call_stack.get("{{topic}}"))
        self.state.payload = str(call_stack.get("{{payload}}"))
        self.state.retain = False
        retain = call_stack.get("{{retain}}")
        if retain == "1" or retain == "True" or retain == "true":
            self.state.retain = True

        self.platform.publish(self.state.topic, self.state.payload, retain = self.state.retain)

        return super().invoke(call_stack)
