from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class PrintActionConfiguration(ActionConfiguration):
    '''Configuration settings for a GPIO output'''
    
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "console"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v

        
class PrintActionState(BaseState):
    '''Represents the state of the Print Action'''

    message: str
    '''Last message'''


class PrintAction(BaseAction):
    '''Prints the given {{payload}} to the System Console.'''
    
    def __init__(self, parent: Stackable, config: PrintActionConfiguration) -> None:
        super().__init__(parent, config)
        self.state = PrintActionState()

    def invoke(self, call_stack: CallStack):

        if self.configuration.variables is not None:
            call_stack.with_keys(self.configuration.variables)        

        message = call_stack.get("{{payload}}")

        print("PRINT: " + str(message))
        self.state = message

        super().invoke(call_stack)
