from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class DFPlayerPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the DFPlayer'''

    @validator('platform')
    def __check_platform(cls, v):
        if "plugins.dfplayer" not in v:
            raise ValueError("wrong platform: plugins.dfplayer, is: " + v)
        return v

    tx_pin: str = "GPIO5"
    '''GPIO pin for TX communication to the DFPlayer Mini'''

    baud_rate: Optional[int] = 9600
    '''Baudrate for the serial interface, 9600 by default'''


class Platform(BasePlatform, Logging):
    '''This platform opens a serial console through the tx_pin to the DFPlayer.
    Use the Action to invoke commands like 'play'. 
    '''

    def __init__(self, parent: Stackable, config: DFPlayerPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

        tx_pin = int(str(self.configuration.tx_pin).replace("GPIO", ""))
        
        try:
            import pigpio
        except Exception as e:
            self.log_error("pigpio library not installed, DFPlayer Mini not initialized")

        try:
            import sys, os

            #find actual path
            realpath = os.path.realpath(__file__)
            dirname = os.path.dirname(realpath)

            #add modules & plugins
            app_path = os.path.join(dirname, "SimpleDFPlayerMini_for_RaspberryPi")
            sys.path.append(app_path)

            from dfplayer import SimpleDFPlayerMini #type: ignore
            self.player = SimpleDFPlayerMini(tx_pin, self.configuration.baud_rate)
            
        except Exception as e:
            self.log_error(e)
            self.player = None
