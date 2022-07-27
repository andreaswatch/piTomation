import json
from sys import platform
import socket
import queue
import threading
from typing import Any, Optional
from pydantic.class_validators import validator

from modules.base.Configuration import *
from modules.base.Instances import *

class BluetoothAvailabilityConfiguration(Configuration):
    '''Availability topic and last will.'''

    topic: str
    '''configured topic for the mqtt client's last will and we also send a message on connect'''

    payload_on: str
    '''payload to send when connected succsessfully'''

    payload_off: str
    '''payload to send when the connection dissapered (last will)'''


@configuration
class BluetoothRelayPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the RFComm server platform.'''

    mac_address: str
    '''The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.'''

    port: int = 1

    type: str
    '''server/client'''

    availability: Optional[BluetoothAvailabilityConfiguration]
    '''Availability topic and last will'''

    on_message: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute when a message is received, see `modules.base.Configuration.AutomationConfiguration`'''  

    on_connected: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute when the connection to the host is established, see `modules.base.Configuration.AutomationConfiguration`'''

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
        self.on_connect = self.__init_on_connect()
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
                print("BT Connection established.")
                self.__publish_available(call_stack)
                self.on_connect()

                while(True):

                    received = client.recv(size)
                    if(received):
                        print("BT got message")
                        self.on_message(client, received)

                    try:
                        while(True):
                            item = self.send_queue.get()
                            print("BT send message")
                            self.socket.sendall(bytes(
                                item, 
                                encoding="utf-8")
                                )
                    except:
                        pass
                        
            thread = threading.Thread(target=loop)
            thread.start()

        else:
            self.socket.connect((self.configuration.mac_address, self.configuration.port))
            print("BT connected")
            self.__publish_available(call_stack)
            self.on_connect()

            def client_loop():
                while(True):

                    try:
                        item = self.send_queue.get()
                        print("BT send message")
                        self.socket.sendall(bytes(
                            item, 
                            encoding="utf-8")
                            )                    
                    except:
                        pass
                            
                    received = self.socket.recv(size)
                    if(received):
                        print("BT got message")
                        self.on_message(self.socket, received)
                        
            thread = threading.Thread(target=client_loop)
            thread.start()           

        super().start(call_stack)

    def __publish_available(self, call_stack):
        def render(var):
            '''this is only to avoid typing errors'''
            return str(call_stack.get(var))

        if self.configuration.availability:
            av = self.configuration.availability

            av_topic = render(av.topic)
            av_payload_on = render(av.payload_on)
            av_payload_off = render(av.payload_off)

            self.subscribe(av_topic)

            av = self.configuration.availability
            self.publish(av_topic, av_payload_on, retain = True)        


    def subscribe(self, topic: str, callback=None):
        if callback is not None:
            self.callbacks.append({"topic": topic, "callback": callback})


    def publish(self, topic: str, payload: Any, retain: bool = False):
        data = {
            "topic": topic,
            "payload": payload,
            "retain": retain
        }
        json_data = json.dumps(data)

        print("BT add to send queue: ")
        print(" - topic: " + topic)
        #print(" data: " + data)

        self.send_queue.put(json_data)


    def __init_on_message(self):
        self.on_message_automations = []
        if self.configuration.on_message:
            for automation in self.configuration.on_message:
                self.on_message_automations.append(Automation(self, automation))

        def method(client, msg):
            jsonstring = msg.decode("utf-8")
            data = json.loads(jsonstring)

            call_stack = CallStack()\
                .with_stack(self.get_full_stack()) \
                .with_keys({
                    "payload": data["payload"],
                    "topic": data["topic"]
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


    def __init_on_connect(self):
        self.on_connected_actions = []
        if self.configuration.on_connected:
            for automationConfig in self.configuration.on_connected:
                self.on_connected_actions.append(Automation(self, automationConfig))

        def method():
            print("BT on_connected")
            
            #TODO:TEST if (rc is not 0):
            #TODO:TEST     sys.exit(0)

            call_stack = CallStack()\
                .with_stack(self.get_full_stack())

            self.__publish_available(call_stack)

            for callback in self.callbacks:
                self.subscribe(callback["topic"])

            for automation in self.on_connected_actions:
                automation.invoke(call_stack)

        return method




    def dispose(self):
        self.socket.close()
        self.socket = None
        return super().dispose()




