
from modules.base.CallStack import CallStack
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class MqttActionConfiguration(ActionConfiguration):
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "mqtt"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class Action(BaseAction):
    from plugins.mqtt.Platform import Platform as MqttPlatform

    def __init__(self, parent: MqttPlatform, config: MqttActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent

    def invoke(self, call_stack: CallStack):
        call_stack = call_stack.with_element(self)

        state = {
            "topic": str(call_stack.get("topic")),
            "payload": str(call_stack.get("payload"))
        }

        self.platform.publish(state["topic"], state["payload"])

        return super().invoke(call_stack)
