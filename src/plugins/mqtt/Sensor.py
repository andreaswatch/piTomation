
from enum import auto
from modules.base.Configuration import *
from modules.base.Instances import *


@configuration
class MqttSensorConfiguration(SensorConfiguration):
    '''Topic to listen to'''
    topic: str

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "mqtt"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v   

    on_message: Optional[list[AutomationConfiguration]] = [] 

class MqttSensorState(BaseState):
    topic: str
    payload: str

class Sensor(BaseSensor):
    '''Allows to listen to a given MQTT topic.'''
    from plugins.mqtt.Platform import Platform

    def __init__(self, parent: Platform, config: MqttSensorConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config
        self.state = MqttSensorState()

        self.on_message_automations = Automation.create_automations(self, config.on_message)

    def start(self, call_stack: CallStack):
        topic = call_stack.get(self.configuration.topic)
        self.parent.subscribe(topic, self.on_message)

    def on_message(self, call_stack: CallStack):
        self.state.topic = str(call_stack.get("{{topic"))
        self.state.payload = str(call_stack.get("{{payload"))

        for automation in self.on_message_automations:
            automation.invoke(call_stack)

        self.on_state_changed(call_stack)
