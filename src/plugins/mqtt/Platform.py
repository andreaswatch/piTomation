import json
from sys import platform
import threading
from typing import Any, Optional
import paho.mqtt.client as mqtt
from pydantic.class_validators import validator

from modules.base.Configuration import *
from modules.base.Instances import *

class MqttAvailabilityConfiguration(Configuration):
    '''Availability topic and last will.'''

    topic: str
    '''configured topic for the mqtt client's last will and we also send a message on connect'''

    payload_on: str
    '''payload to send when connected succsessfully'''

    payload_off: str
    '''payload to send when the connection dissapered (last will)'''


@configuration
class MqttPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the MQTT platform.'''

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.mqtt" not in v:
            raise ValueError("wrong platform: plugins.mqtt, is: " + v)
        return v

    host: str
    '''MQTT server address'''

    port: int
    '''MQTT server port'''

    keep_alive: Optional[int] = 60
    '''seconds to keep the server connection'''

    availability: Optional[MqttAvailabilityConfiguration]
    '''Availability topic and last will'''

    on_connected: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute when the connection to the host is established, see `modules.base.Configuration.AutomationConfiguration`'''

    on_disconnected: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute when the connection to the host is lost, see `modules.base.Configuration.AutomationConfiguration`'''   

    on_message: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute when a MQTT message is received, see `modules.base.Configuration.AutomationConfiguration`'''  


class Platform(BasePlatform):
    '''MQTT Platform'''

    def __init__(self, parent: Stackable, config: MqttPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.app = parent.get_app()
        self.configuration = config
        self.initialized = False

        self.callbacks = []

    def __publish_available(self, call_stack):
        def render(var):
            '''this is only to avoid typing errors'''
            return str(call_stack.get(var))

        if self.configuration.availability:
            av = self.configuration.availability

            av_topic = render(av.topic)
            av_payload_on = render(av.payload_on)
            av_payload_off = render(av.payload_off)

            self.client.will_set(av_topic, av_payload_off)
            self.client.subscribe(av_topic)

            av = self.configuration.availability
            self.publish(av_topic, av_payload_on, retain = True)        

    def __connect(self, call_stack):
        if not self.initialized:
            print("MQTT Client not initialized, cancel 'connect'")
            return

        def render(var):
            '''this is only to avoid typing errors'''
            return str(call_stack.get(var))

        self.client.connect(self.configuration.host, self.configuration.port, self.configuration.keep_alive)

        self.__publish_available(call_stack)


    def start(self, call_stack: CallStack):
        def render(var):
            '''this is only to avoid typing errors'''
            return str(call_stack.get(var))

        client_name = "PiTomation" + "_" + self.app.device.configuration.name
        print("MQTT Client Name: " + client_name)
        self.client = mqtt.Client(client_name, clean_session = True) #type: ignore
        self.client.on_connect = self.__init_on_connect()
        self.client.on_disconnect = self.__init_on_disconnect()
        self.client.on_message = self.__init_on_message()
        self.initialized = True
        self.__connect(call_stack)

        def loop():
            self.client.loop_start()

        loop_thread = threading.Thread(target=loop)
        loop_thread.start()

        super().start(call_stack)


    def dispose(self):
        self.client.loop_stop()
        return super().dispose()


    def __init_on_message(self):
        self.on_message_automations = []
        if self.configuration.on_message:
            for automation in self.configuration.on_message:
                self.on_message_automations.append(Automation(self, automation))

        def method(client, userdata, msg):
            payload = msg.payload.decode("utf-8")
            try:
                payload = json.loads(payload)
            except:
                payload = str(payload)

            call_stack = CallStack()\
                .with_stack(self.get_full_stack()) \
                .with_keys({
                    "payload": payload,
                    "topic": msg.topic
                })

            for callback in self.callbacks:
                if callback["topic"] == msg.topic:
                    callback["callback"](call_stack)
                elif str(callback["topic"]).endswith("+") or str(callback["topic"]).endswith("#"):
                    if str(msg.topic).startswith(str(callback["topic"])[0:-2]):
                        callback["callback"](call_stack)

            for automation in self.on_message_automations:
                automation.invoke(call_stack)

        return method

    def __init_on_disconnect(self):
        self.on_disconnect_actions = []
        if self.configuration.on_disconnected:
            for automation in self.configuration.on_disconnected:
                self.on_disconnect_actions.append(Automation(self, automation))

        def method(client, userdata, flags):
            print("MQTT disconnected!")
            
            call_stack = CallStack()\
                .with_stack(self.get_full_stack()) \
                .with_key("flags", flags)

            for automation in self.on_disconnect_actions:
                automation.invoke(call_stack)

        return method

    def __init_on_connect(self):
        self.on_connected_actions = []
        if self.configuration.on_connected:
            for automationConfig in self.configuration.on_connected:
                self.on_connected_actions.append(Automation(self, automationConfig))

        def method(client, userdata, flags, rc):
            print("MQTT connection state: " + str(rc))
            print("  if rc=0, the client is connected.")
            
            #TODO:TEST if (rc is not 0):
            #TODO:TEST     sys.exit(0)

            call_stack = CallStack()\
                .with_stack(self.get_full_stack()) \
                .with_key("return_code", rc)

            self.__publish_available(call_stack)

            for callback in self.callbacks:
                self.client.subscribe(callback["topic"])

            for automation in self.on_connected_actions:
                automation.invoke(call_stack)

        return method


    def subscribe(self, topic: str, callback=None):
        if callback is not None:
            self.callbacks.append({"topic": topic, "callback": callback})

        self.client.subscribe(topic)


    def publish(self, topic: str, payload: Any, retain: bool = False):
        if type(payload) is dict:
            payload = json.dumps(payload)
        else:
            #unexpected type, just send it as string
            payload = str(payload)

        self.client.publish(topic, payload, qos = 1, retain = retain)


