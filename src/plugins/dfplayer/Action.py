import time
from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.dfplayer.Platform import Platform
import threading


@configuration
class DFPlayerActionConfiguration(ActionConfiguration):
    '''Configuration settings for the DFPlayer'''

    @validator('platform')
    def check_platform(cls, v):
        platform_name = "dfplayer"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class DfPlayerState(BaseState):
    '''Represents the state of the DFPlayer'''

    is_playing = False
    '''Actually, there is only a TX connection implemented, paytime is hardcoded to 5s'''


class Action(BaseAction, Logging):
    '''To invoke this action, pass this values:
    values:
        - command: set_vol
        - volume: 30
    or, values:
        - command: next_track
    '''

    def __init__(self, parent: Platform, config: DFPlayerActionConfiguration) -> None:
        super().__init__(parent, config)
        self.platform = parent
        self.player = parent.player

        self.state = DfPlayerState()

    def invoke(self, call_stack: CallStack):

        if self.configuration.variables is not None:
            call_stack.with_keys(self.configuration.variables)

        self.state.is_playing = True
        self.on_state_changed(call_stack) 

        command_name = call_stack.get("{{command}}")

        if type(command_name) is str:
            if hasattr(self.player, command_name):
                method = getattr(self.player, command_name)

                if command_name == "set_vol":
                    method(call_stack.get("{{volume}}"))
                elif command_name == "set_eq":
                    method(call_stack.get("{{equalizer}}"))      
                elif command_name == "set_mode":
                    method(call_stack.get("{{mode}}"))       
                elif command_name == "set_folder":
                    method(call_stack.get("{{folder_index}}"))           
                else:
                    method()           
            else:
                self.log_error("Unknown command: " + command_name)
        else:
            self.log_error("Unknown command: " + str(command_name))

        super().invoke(call_stack)

        def update_state_delayed():
            time.sleep(5)
            self.state.is_playing = False
            self.on_state_changed(call_stack) 

        loop_thread = threading.Thread(target=update_state_delayed)
        loop_thread.start()        



        