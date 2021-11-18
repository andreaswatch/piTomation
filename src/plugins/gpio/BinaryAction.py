from enum import Enum
from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.gpio.Platform import Platform

@configuration
class BinaryActionConfiguration(ActionConfiguration):
    '''Configuration settings for a GPIO output'''

    pin: str
    '''GPIO PIN name. e.g. GPIO22'''

    on_high: list[AutomationConfiguration] = []
    '''List of Automations to execute when the GPIO is triggered to high, see `AutomationConfiguration`'''

    on_low: list[AutomationConfiguration] = []
    '''List of Automations to execute when the GPIO is triggered to low, see `AutomationConfiguration`'''

    active_high: bool = True
    '''"True=normal, False=inverted'''

    initial_value: bool = False
    '''expected initial value'''

    @validator('platform')
    def __check_platform(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class BinaryActionState(BaseState):
    '''Represents the state of the GPIO pin'''

    is_high = False
    '''Returns if the LED is HIGH(True) or LOW(False)'''


class BinaryActionCommands(Enum):
    '''Available commands to control the GPIO Pin'''

    on = "on"
    '''Turn the LED on'''

    off = "off"
    '''Turn the LED off'''

    toggle = "toggle"
    '''Toggle on/off'''


class BinaryAction(BaseAction, Debuggable, Logging):
    '''Control the state of a GPIO pin'''

    def __init__(self, parent: Platform, config: BinaryActionConfiguration) -> None:
        super().__init__(parent, config)

        self.gpio = parent.gpio
        self.configuration = config
        self.state = BinaryActionState()

        self.output_pin = self.gpio.DigitalOutputDevice(
            pin = self.configuration.pin,
            active_high = self.configuration.active_high,
            initial_value = self.configuration.initial_value
        )

        self.on_high = Automation.create_automations(self, config.on_high)
        self.on_low = Automation.create_automations(self, config.on_low)


    def invoke(self, call_stack: CallStack):
        topic = str(call_stack.get("{{topic}}"))
        self.log_debug("Command: " + topic)

        call_stack = call_stack.with_element(self)

        if BinaryActionCommands.on.name == topic:
            self.output_pin.on()
            self.state.is_high = True
            for on_high in self.on_high:
                on_high.invoke(call_stack)

        elif BinaryActionCommands.off.name == topic:
            self.output_pin.off()
            self.state.is_high = False
            for on_low in self.on_low:
                on_low.invoke(call_stack)

        elif BinaryActionCommands.toggle.name == topic:
            self.output_pin.toggle()
            if self.output_pin.is_active:
                self.state.is_high = True
                for on_high in self.on_high:
                    on_high.invoke(call_stack)
            else:
                self.state.is_high = False
                for on_low in self.on_low:
                    on_low.invoke(call_stack)

        else:
            self.log_error("Unknown command: {{" + topic + "}}")

        super().invoke(call_stack)

