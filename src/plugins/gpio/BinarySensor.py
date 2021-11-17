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
    def __check_platform(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

    @validator('type')
    def __check_type(cls, v):
        type_name = "BinarySensor"
        if v != type_name:
            raise ValueError("wrong type: " + type_name + ", is: " + v)
        return v          

class BinaryState(BaseState):
    '''Represents the state of the GPIO pin'''

    is_high = False
    '''Returns if the GPIO pin is HIGH(True) or LOW(False)'''


class BinarySensor(BaseSensor, Debuggable):
    '''Read the state of a GPIO pin'''
    
    def __init__(self, parent: Platform, config: BinarySensorConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config
        self.state = BinaryState()

        self.input_device = DigitalInputDevice(
            pin = self.configuration.pin,
            pull_up = self.configuration.pull_up,
            active_state = self.configuration.active_state,
            bounce_time = self.configuration.bounce_time,
        )

        self.on_high_automations = Automation.create_automations(self, self.configuration.on_high)
        self.on_low_automations = Automation.create_automations(self, self.configuration.on_low)
        
        self.input_device.when_activated = Handler(self, self.on_high_automations, True).invoke
        self.input_device.when_deactivated = Handler(self, self.on_low_automations, False).invoke

class Handler():
    def __init__(self, binary_sensor: BinarySensor, automations: list[Automation], is_pressed) -> None: #type: ignore
        self.automations = automations
        self.is_pressed = is_pressed
        self.binary_sensor = binary_sensor

    def invoke(self):
        self.binary_sensor.state.is_high = self.is_pressed
        call_stack = CallStack().with_element(self)

        for automation in self.automations:
            automation.invoke(call_stack)

        self.binary_sensor.on_state_changed(call_stack)