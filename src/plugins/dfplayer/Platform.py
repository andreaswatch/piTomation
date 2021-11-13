from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class DFPlayerPlatformConfiguration(PlatformConfiguration):

    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.dfplayer" not in v:
            raise ValueError("wrong platform: plugins.dfplayer, is: " + v)
        return v

    tx_pin: str = "GPIO5"
    '''GPIO pin for TX communication to the DFPlayer Mini'''

    baud_rate: Optional[int] = 9600
    '''Baudrate for the serial interface, 9600 by default'''

class Platform(BasePlatform, Logging):
    def __init__(self, parent: Stackable, config: DFPlayerPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

        try:
            import pigpio
            from plugins.dfplayer.SimpleDFPlayerMini_for_RaspberryPi.dfplayer import SimpleDFPlayerMini
            self.player = SimpleDFPlayerMini(self.configuration.tx_pin, self.configuration.baud_rate)
        except:
            self.log_error("pigpio library not installed, DFPlayer Mini not initialized")
            self.player = None
