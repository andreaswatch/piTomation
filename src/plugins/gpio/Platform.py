import gpiozero as gpiozero
from pydantic.class_validators import validator

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class GpioPlatform(PlatformConfiguration):

    platform: str

    factory: str = "pigpio"
    '''gpio zero factory name, please see https://gpiozero.readthedocs.io/en/stable/api_pins.html'''
    
    @validator('platform')
    def check_platform_module(cls, v):
        if "plugins.gpio" not in v:
            raise ValueError("wrong platform: plugins.gpio, is: " + v)
        return v


class Platform(BasePlatform):
    def __init__(self, parent: Stackable, config: GpioPlatform) -> None:
        super().__init__(parent, config)
        self.configuration = config

        def mockFactory():
            from gpiozero.pins.mock import MockFactory
            return MockFactory()

        def rpigpioFactory():
            from gpiozero.pins.rpigpio import RPiGPIOFactory
            return RPiGPIOFactory()

        def lgpioFactory():
            from gpiozero.pins.lgpio import LGPIOFactory
            return LGPIOFactory()

        def rpioFactory():
            from gpiozero.pins.rpio import RPIOFactory
            return RPIOFactory()

        def pigpioFactory():
            from gpiozero.pins.pigpio import PiGPIOFactory
            return PiGPIOFactory()

        def nativeFactory():
            from gpiozero.pins.native import NativeFactory
            return NativeFactory()


        factories = {
            "mock": mockFactory,
            "rpigpio": rpigpioFactory,
            "lgpio": lgpioFactory,
            "rpio": rpioFactory,
            "pigpio": pigpioFactory,
            "native":	nativeFactory
        }

        gpiozero.Device.pin_factory = factories[self.configuration.factory]

        self.GPIO = gpiozero

    def dispose(self):
        self.GPIO.Device.close()
        super().dispose()
