from os import execv
from gpiozero.input_devices import DigitalInputDevice
from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.gpio.Platform import Platform
from dataclasses import dataclass


@configuration
class BinarySensorConfiguration(SensorConfiguration):
    '''Sensor to read the state of a GPIO pin.'''

    pin: str
    '''GPIO PIN name. e.g. GPIO22'''

    pull_up: Optional[bool] = True
    '''True=enable software pull up, False=enable software pulldown, None=disabled(floating)'''

    active_state: Optional[bool] = None
    '''True: Active=HIGH, False: Active=LOW, None=auto-select with pull_up not None'''

    bounce_time: Optional[int] = None
    '''Length of time (in seconds) to ignore changes after initial change'''

    on_high: list[AutomationConfiguration] = []
    '''Automations to invoke when the GPIO is set to HIGH'''
    
    on_low: list[AutomationConfiguration] = []
    '''Automations to invoke when the GPIO is set to HIGH'''

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

    @validator('type')
    def check_type(cls, v):
        type_name = "BinarySensor"
        if v != type_name:
            raise ValueError("wrong type: " + type_name + ", is: " + v)
        return v          

class BinaryState(BaseState):
    is_high = False

class BinarySensor(BaseSensor, Debuggable):
    '''Read the state of a GPIO pin'''
    
    def __init__(self, parent: Platform, config: BinarySensorConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config
        self.state = BinaryState()

        self.__input_device = DigitalInputDevice(
            pin = self.configuration.pin,
            pull_up = self.configuration.pull_up,
            active_state = self.configuration.active_state,
            bounce_time = self.configuration.bounce_time,
        )

        class exec():
            def __init__(cls, automations: list[Automation], is_pressed) -> None: #type: ignore
                cls.automations = automations
                cls.is_pressed = is_pressed

            def invoke(cls): #type: ignore
                self.state.is_high = cls.is_pressed
                call_stack = CallStack().with_keys({
                    "is_active": self.__input_device.is_active,
                    "pin": self.__input_device.pin,
                    "pull_up": self.__input_device.pull_up,
                    "value": self.__input_device.value,
                })

                for automation in cls.automations:
                    automation.invoke(call_stack)

                self.on_state_changed(call_stack)


        self.on_high_automations = Automation.create_automations(self, self.configuration.on_high)
        self.on_low_automations = Automation.create_automations(self, self.configuration.on_low)
        
        self.__input_device.when_activated = exec(self.on_high_automations, True).invoke
        self.__input_device.when_deactivated = exec(self.on_low_automations, False).invoke
