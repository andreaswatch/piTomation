import json
from sys import platform
import threading
from typing import Optional
from marshmallow.validate import Equal
import paho.mqtt.client as mqtt
from pydantic.class_validators import validator
from pydantic.main import BaseModel

from modules.app.base.Configuration import *
from modules.app.base.Instances import *

class Availability(BaseModel):
    topic: str
    '''configured topic for the mqtt client's last will and we also send a message on connect'''

    payload_on: str
    '''payload to send when connected succsessfully'''

    payload_off: str
    '''payload to send when the connection dissapered (last will)'''


@configuration
class MqttPlatformConfiguration(PlatformConfiguration):

    platform: str
    
    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.mqtt" not in v:
            raise ValueError("wrong platform: plugins.mqtt, is: " + v)
        return v

    host: str
    '''MQTT server address'''

    port: int
    '''MQTT server port'''

    keep_alive: Optional[int] = 60
    '''seconds to keep the server connection'''

    availability: Optional[Availability]

    on_connected: Optional[list[AutomationConfiguration]] = []
    '''Actions to execute when the connection to the host is established''' 

    on_disconnected: Optional[list[AutomationConfiguration]] = []
    '''Actions to execute when the connection to the host is lost'''    

    on_message: Optional[list[AutomationConfiguration]] = []
    '''Actions to execute when a MQTT message is received'''    


class Platform(BasePlatform):
    def __init__(self, parent: Stackable, config: MqttPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.app = parent.get_app()
        self.configuration = config
        self.callbacks = []

        self.is_connected = False

        self.client = mqtt.Client(self.app.id + "_" + self.app.device.configuration.name)
        self.client.on_connect = self.__init_on_connect()
        self.client.on_disconnect = self.__init_on_disconnect()
        self.client.on_message = self.__init_on_message()


        if self.configuration.availability:
            av = self.configuration.availability
            self.client.will_set(av.topic, av.payload_off)
            self.client.subscribe(av.topic)

        self.client.connect(self.configuration.host, self.configuration.port, self.configuration.keep_alive)

        if self.configuration.availability:
            av = self.configuration.availability
            self.publish(av.topic, av.payload_on)


    def start(self):
        def loop():
            self.client.loop_forever()

        loop_thread = threading.Thread(target=loop)
        loop_thread.start()

        super().start()


    def dispose(self):
        self.client.loop_stop()
        return super().dispose()


    def get_variable_value(self, text: str):
        t = str(text).lower()
        if t == "connected":
            return self.is_connected

        return super().get_variable_value(text)


    def __init_on_message(self):
        self.on_message_automations = []
        for automation in self.configuration.on_message:
            self.on_message_automations.append(Automation(self, automation))

        def method(client, userdata, msg):
            payload = msg.payload.decode("utf-8")

            call_stack = CallStack(from_list=self.get_full_stack()) \
                .with_key("payload", payload) \
                .with_key("topic", msg.topic)

            for callback in self.callbacks:
                if callback["topic"] == msg.topic:
                    callback["callback"](call_stack)

            for automation in self.on_message_automations:
                automation.invoke(call_stack)

        return method

    def __init_on_disconnect(self):
        self.on_disconnect_actions = []
        for automation in self.configuration.on_disconnected:
            self.on_disconnect_actions.append(Automation(self, automation))

        def method(client, userdata, flags):
            self.is_connected = False

            call_stack = CallStack(from_list=self.get_full_stack()) \
                .with_key("flags", flags)

            for automation in self.on_disconnect_actions:
                automation.invoke(call_stack)

        return method

    def __init_on_connect(self):
        self.on_connected_actions = []
        for automationConfig in self.configuration.on_connected:
            self.on_connected_actions.append(Automation(self, automationConfig))

        def method(client, userdata, flags, rc):
            self.is_connected = True

            call_stack = CallStack(from_list=self.get_full_stack()) \
                .with_key("return_code", rc)

            for automation in self.on_connected_actions:
                automation.invoke(call_stack)

        return method


    def subscribe(self, topic: str, callback=None):
        self.callbacks.append({"topic": topic, "callback": callback})
        self.client.subscribe(topic)


    def publish(self, topic: str, payload: str, retain=True):
        if type(payload) is dict:
            payload = json.dumps(payload)

        self.client.publish(topic, payload, qos=1, retain=retain)
