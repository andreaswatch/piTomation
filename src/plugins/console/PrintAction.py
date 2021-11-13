from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class PrintActionConfiguration(ActionConfiguration):
    
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "console"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v
        

class PrintAction(BaseAction):
    '''prints the given payload to the console'''
    
    def __init__(self, parent: Stackable, config: PrintActionConfiguration) -> None:
        super().__init__(parent, config)

    def invoke(self, call_stack: CallStack):

        message = call_stack.get("{{payload}}")

        print("PRINT: " + str(message))

        super().invoke(call_stack)
