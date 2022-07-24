import json
from sys import platform
import threading
from typing import Any, Optional
from pydantic.class_validators import validator
import bluetooth

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class RfcommServerPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the RFComm server platform.'''

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.rfcomm_server" not in v:
            raise ValueError("wrong platform: plugins.mqtt, is: " + v)
        return v

class Platform(BasePlatform):
    '''RFComm Server Platform'''

    def __init__(self, parent: Stackable, config: RfcommServerPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.app = parent.get_app()
        self.configuration = config
        self.initialized = False
        self.sock = None
        self.callbacks = []

    def start(self, call_stack: CallStack):
        def start_task():
            server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            server_sock.bind(("", bluetooth.PORT_ANY))
            server_sock.listen(1)

            port = server_sock.getsockname()[1]

            uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

            bluetooth.advertise_service(server_sock, "PiTomationServer", service_id=uuid,
                                        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                        profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                        # protocols=[bluetooth.OBEX_UUID]
                                        )

            print("Waiting for connection on RFCOMM channel", port)

            while true:
                client_sock, client_info = server_sock.accept()
                print("Accepted connection from", client_info)


        thread = threading.Thread(target=start_task)
        thread.start()
        
        super().start(call_stack)
        

    def publish(self, payload):
        sock.send(data)

    def dispose(self):
        self.sock.close()
        self.sock = None
        return super().dispose()




