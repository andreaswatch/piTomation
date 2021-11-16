from sys import platform
from pydantic.class_validators import validator
import pywebio.input as IN
import pywebio.output as OUT
import time
import threading

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class WebPlatformConfiguration(PlatformConfiguration):
    '''WebApp Platform based on pywebio.'''

    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.web" not in v:
            raise ValueError("wrong platform: plugins.web, is: " + v)
        return v

class Platform(BasePlatform):
    '''WebApp Platform based on pywebio.'''

    def __init__(self, parent: Stackable, config: PlatformConfiguration) -> None:
        super().__init__(parent, config)
        
        self.logs = [["Logs"]]
        self.table = [["Topic", "Payload"]]
        self.has_been_updated = True
        self.has_started = False


    def update(self, topic, payload):
        while not self.has_started:
            time.sleep(1)

        for line in self.table:
            if line[0] == topic:
                line[1] = payload
                self.has_been_updated = True
                return

        self.table.append([topic, payload])        
        self.has_been_updated = True


    def add_log(self, text):
        while not self.has_started:
            time.sleep(1)

        self.logs.append([text])
        self.has_been_updated = True


    def start(self, call_stack: CallStack):
        def loop():
            OUT.set_scope('result')
            while True:
                if self.has_been_updated:
                    self.has_been_updated = False
                    with OUT.use_scope('result', clear=True):
                        OUT.put_markdown(" ## Table")
                        OUT.put_table(self.table)
                        OUT.put_markdown(" ## Logs")
                        OUT.put_table(self.logs)
                time.sleep(0.2)
                
        
        loop_thread = threading.Thread(target=loop)
        loop_thread.start()
        super().start(call_stack)
        self.has_started = True

