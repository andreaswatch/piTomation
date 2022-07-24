import json
from sys import platform
import threading
from typing import Any, Optional
from pydantic.class_validators import validator
import bluetooth


from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class RfcommClientPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the RFComm client platform.'''

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.rfcomm_client" not in v:
            raise ValueError("wrong platform: plugins.mqtt, is: " + v)
        return v

    server: str
    '''The server's MAC address'''


class Platform(BasePlatform):
    '''RFComm Client Platform'''

    def __init__(self, parent: Stackable, config: RfcommClientPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.app = parent.get_app()
        self.configuration = config
        self.initialized = False
        self.sock = None
        self.callbacks = []

    def connect(self):
        if not self.initialized:
            print("RFComm Client not initialized, cancel 'connect'")
            return

        addr = str(self.configuration.server)

        if (len(addr) == 0):
            print("RFComm Client is empty, cancel 'connect'")
            return

        # search for the server service
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        service_matches = bluetooth.find_service(uuid=uuid, address=addr)

        if len(service_matches) == 0:
            print("Couldn't find the SampleServer service.")
            return

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        print("Connecting to \"{}\" on {}".format(name, host))

        # Create the client socket
        self.sock.connect((host, port))

        print("RfComm connected.")


    def start(self, call_stack: CallStack):
        def render(var):
            '''this is only to avoid typing errors'''
            return str(call_stack.get(var))


        if not self.configuration.server:
            print("RFComm Client not defined, cancel 'connect'")
            return

        def start_task():
            while(True):
                if self.sock is None:
                    self.initialized = False
                    self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.initialized = True
                    self.connect()


        thread = threading.Thread(target=start_task)
        thread.start()
        
        super().start(call_stack)
        

    def publish(self, payload):
        sock.send(data)

    def dispose(self):
        self.sock.close()
        self.sock = None
        return super().dispose()




