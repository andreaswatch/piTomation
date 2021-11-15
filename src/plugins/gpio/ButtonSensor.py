from os import execv
from gpiozero.input_devices import Button
from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.gpio.Platform import Platform
from dataclasses import dataclass


@configuration
class ButtonSensorConfiguration(SensorConfiguration):
    '''Sensor to read the GPIO state of a typical button.'''

    pin: str
    '''GPIO PIN name. e.g. GPIO22'''

    pull_up: Optional[bool] = True
    '''True=enable software pull up, False=enable software pulldown, None=disabled(floating)'''

    active_state: Optional[bool] = None
    '''True: Active=HIGH, False: Active=LOW, None=auto-select with pull_up not None'''

    bounce_time: Optional[int] = None
    '''Length of time (in seconds) to ignore changes after initial change'''

    hold_time: int = 1
    '''Length of time (in seconds) to wait after the button is pushed, until executing the when_held handler'''

    hold_repeat: Optional[bool] = False
    '''If True, the when_held handler will be repeatedly executed as long as the device remains active, every hold_time seconds. If False (the default) the when_held handler will be only be executed once per hold.'''

    on_hold: list[AutomationConfiguration] = []
    
    on_press: list[AutomationConfiguration] = []
    
    on_release: list[AutomationConfiguration] = []

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class ButtonState(BaseState):
    is_pressed = False

class ButtonSensor(BaseSensor, Debuggable):
    '''Read the state of a GPIO pin'''
    
    def __init__(self, parent: Platform, config: ButtonSensorConfiguration) -> None:
        super().__init__(parent, config)
        self.GPIO = parent.GPIO
        self.configuration = config
        self.state = ButtonState()

        self.Button = Button(
            pin = self.configuration.pin,
            pull_up = self.configuration.pull_up,
            active_state = self.configuration.active_state,
            bounce_time = self.configuration.bounce_time,
            hold_time = self.configuration.hold_time,
            hold_repeat = self.configuration.hold_repeat
        )

        class exec():
            def __init__(cls, automations: list[Automation], is_pressed) -> None:
                cls.automations = automations
                cls.is_pressed = is_pressed

            def invoke(cls):
                self.state.is_pressed = cls.is_pressed
                call_stack = CallStack().with_keys({
                    "held_time": self.Button.held_time,
                    "hold_repeat": self.Button.hold_repeat,
                    "hold_time": self.Button.hold_time,
                    "is_held": self.Button.is_held,
                    "is_active": self.Button.is_active,
                    "pin": self.Button.pin,
                    "pull_up": self.Button.pull_up,
                    "value": self.Button.value,
                })

                for automation in cls.automations:
                    automation.invoke(call_stack)

                self.on_state_changed(call_stack)


        self.on_press_automations = Automation.create_automations(self, self.configuration.on_press)
        self.on_hold_automations = Automation.create_automations(self, self.configuration.on_hold)
        self.on_release_automations = Automation.create_automations(self, self.configuration.on_release)
        
        self.Button.when_activated = exec(self.on_press_automations, True).invoke
        self.Button.when_held = exec(self.on_hold_automations, True).invoke
        self.Button.when_deactivated = exec(self.on_release_automations, False).invoke
