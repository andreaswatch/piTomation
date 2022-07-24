import os
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class ShellCommandActionConfiguration(ActionConfiguration):
    '''Configuration settings for the ShellCommand Action'''
    
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "console"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v

        
class ShellCommandActionState(BaseState):
    '''Represents the state of the ShellCommand Action'''

    pass

class ShellCommandAction(BaseAction, Debuggable):
    '''ShellCommand executes the command in {{{topic}}} with the parameters in {{{payload}}}'''
    
    def __init__(self, parent: Stackable, config: ShellCommandActionConfiguration) -> None:
        super().__init__(parent, config)
        self.state = ShellCommandActionState()
        self.parent = parent

    def invoke(self, call_stack: CallStack):
        command = str(call_stack.get("{{{topic}}}"))
        args = str(call_stack.get("{{{payload}}}"))
        cmdline = command + " " + args

        self.log_debug("Execute shell command: " + cmdline)

        os.system(cmdline)

        super().invoke(call_stack)
