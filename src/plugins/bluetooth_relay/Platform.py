import json
from sys import platform
import socket
import queue
import threading
from typing import Any, Optional
from pydantic.class_validators import validator

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class BluetoothRelayPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the RFComm server platform.'''

    mac_address: str
    '''The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.'''

    port: int = 1

    type: str
    '''server/client'''

    on_message: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute when a message is received, see `modules.base.Configuration.AutomationConfiguration`'''  

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.bluetooth_relay" not in v:
            raise ValueError("wrong platform: plugins.mqtt, is: " + v)
        return v

class Platform(BasePlatform):
    '''Bluetooth Relay Platform'''

    def __init__(self, parent: Stackable, config: BluetoothRelayPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.app = parent.get_app()
        self.configuration = config
        self.on_message = self.__init_on_message()
        self.socket = None
        self.callbacks = []
        self.send_queue = queue.Queue()

    def start(self, call_stack: CallStack):
        backlog = 1
        size = 1024

        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        if (self.configuration.type == "server"):
            self.socket.bind((self.configuration.mac_address, self.configuration.port))        
            self.socket.listen(backlog)

        def loop():
            client, address = self.socket.accept()
            while(true):

                received = client.recv(size)
                if(received):
                    self.on_message(client, msg)

                if (len(self.send_queue) > 0):
                    sockset.sendall(bytes(
                        self.send_queue.get(), 
                        encoding="utf-8")
                        )
                    
        thread = threading.Thread(target=loop)
        thread.start()

        super().start(call_stack)

    def subscribe(self, topic: str, callback=None):
        if callback is not None:
            self.callbacks.append({"topic": topic, "callback": callback})


    def publish(self, topic, payload):
        data = {
            "topic": topic,
            "payload": payload
        }
        json_data = json.dumps(data)

        self.send_queue.put(json_data)


    def __init_on_message(self):
        self.on_message_automations = []
        if self.configuration.on_message:
            for automation in self.configuration.on_message:
                self.on_message_automations.append(Automation(self, automation))

        def method(client, msg):
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

    def dispose(self):
        self.socket.close()
        self.socket = None
        return super().dispose()




