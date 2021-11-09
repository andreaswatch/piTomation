from os import execv
from gpiozero.input_devices import Button
from modules.app.base.Configuration import *
from modules.app.base.Instances import *
from plugins.gpio.Platform import Platform
from dataclasses import dataclass


@configuration
class ButtonSensorConfiguration(SensorConfiguration):
    pin: str
    '''GPIO PIN name. e.g. GPIO22'''

    pull_up: Optional[bool] = True
    '''True=enable software pullup, False=enable software pulldown, None=disabled(floating)'''

    active_state: Optional[bool] = True
    '''True: Active=HIGH, False: Active=LOW, None=auto-select with pull_up not None'''

    bounce_time: Optional[int] = None
    '''Length of time (in seconds) to ignore changes adter initial change'''

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


class ButtonSensor(BaseSensor, Debuggable):
    def __init__(self, parent: Platform, config: ButtonSensorConfiguration) -> None:
        super().__init__(parent, config)
        self.GPIO = parent.GPIO
        self.configuration = config

        self.Button = Button(
            pin = self.configuration.pin,
            pull_up = self.configuration.pull_up,
            active_state = self.configuration.active_state,
            bounce_time = self.configuration.bounce_time,
            hold_time = self.configuration.hold_time,
            hold_repeat = self.configuration.hold_repeat
        )

        def exec(automations: list[Automation]):
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

            for automation in automations:
                automation.invoke(call_stack)

            for automation in self.on_state_changed_automations:
                automation.invoke(call_stack)


        self.on_press_automations = self._create_automations(self.configuration.on_press)
        self.on_hold_automations = self._create_automations(self.configuration.on_hold)
        self.on_release_automations = self._create_automations(self.configuration.on_release)

        self.Button.when_activated = exec(self.on_press_automations)
        self.Button.when_held = exec(self.on_hold_automations)
        self.Button.when_deactivated = exec(self.on_release_automations)
