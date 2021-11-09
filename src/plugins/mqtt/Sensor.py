
from enum import auto
from modules.app.base.Configuration import *
from modules.app.base.Instances import *


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


class Sensor(BaseSensor):
    from plugins.mqtt.Platform import Platform

    def __init__(self, parent: Platform, config: MqttSensorConfiguration) -> None:
        super().__init__(parent, config)

        self.on_message_automations = self._create_automations(config.on_message)

        parent.subscribe(config.topic, self.on_message)


    def on_message(self, call_stack: CallStack):
        for automation in self.on_message_automations:
            automation.invoke(call_stack)

        self.on_state_changed(call_stack)
