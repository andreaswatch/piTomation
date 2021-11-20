from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class SetVariableActionConfiguration(ActionConfiguration):
    '''Configuration settings for the SetVariable Action'''
    
    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "console"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v

        
class SetVariableActionState(BaseState):
    '''Represents the state of the SetVariable Action'''

    pass

class SetVariableAction(BaseAction, Debuggable):
    '''SetVariable copies the given {{{payload}}} into the variable adressed in id(app).variables.{{topic}}.'''
    
    def __init__(self, parent: Stackable, config: SetVariableActionConfiguration) -> None:
        super().__init__(parent, config)
        self.state = SetVariableActionState()
        self.parent = parent

    def invoke(self, call_stack: CallStack):
        var_name = call_stack.get("{{{topic}}}")
        value = call_stack.get("{{{payload}}}")

        app: BaseApp
        for item in call_stack:
            if hasattr(item, "get_app"):
                app = item.get_app()
                if type(app) is BaseApp:
                    break

        app.variables[var_name] = value

        self.log_debug("Set: id(app).variables." + str(var_name) + " to: " + str(value))

        super().invoke(call_stack)
