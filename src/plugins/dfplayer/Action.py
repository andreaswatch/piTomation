from modules.app.base.Configuration import *
from modules.app.base.Instances import *
from plugins.dfplayer.Platform import Platform


@configuration
class DFPlayerActionConfiguration(ActionConfiguration):
    '''To invoke this action, pass this values:
    values:
        - command: set_vol
        - volume: 30
    or, values:
        - command: next_track
    '''

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "dfplayer"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class Action(BaseAction):
    def __init__(self, parent: Platform, config: DFPlayerActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.player = parent.player

    def invoke(self, call_stack: CallStack):

        if self.configuration.variables is not None:
            call_stack.with_keys(self.configuration.variables)

        command_name = call_stack.get("{{command}}")

        if type(command_name) is str:
            if hasattr(self.player, command_name):
                method = getattr(self.player, command_name)

                if command_name == "set_vol":
                    method(call_stack.get("volume"))
                elif command_name == "set_eq":
                    method(call_stack.get("equalizer"))      
                elif command_name == "set_mode":
                    method(call_stack.get("mode"))       
                elif command_name == "set_folder":
                    method(call_stack.get("folder_index"))           
                else:
                    method()                                                          

        super().invoke(call_stack)



        