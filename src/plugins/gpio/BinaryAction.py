from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.gpio.Platform import Platform


@configuration
class BinaryActionConfiguration(ActionConfiguration):
    '''Action that allows to update the state of a GPIO pin. 
    Available commands: turn_on, turn_off & toggle.
    Use {{topic}} for the command, like:
    values:
      topic: toggle
    '''

    pin: str
    '''GPIO PIN name. e.g. GPIO22'''

    on_high: list[AutomationConfiguration] = []
    '''List of Automations to execute when the GPIO is triggered to high'''

    on_low: list[AutomationConfiguration] = []
    '''List of Automations to execute when the GPIO is triggered to low'''

    active_high: bool = True
    '''"True=normal, False=inverted'''

    initial_value: bool = False
    '''expected initial value'''

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    

class BinaryActionState(BaseState):
    is_high = False


class BinaryAction(BaseAction):
    '''Update the state of a GPIO pin'''

    def __init__(self, parent: Platform, config: BinaryActionConfiguration) -> None:
        super().__init__(parent, config)

        self.__gpio = parent.gpio
        self.configuration = config
        self.state = BinaryActionState()

        self.output_pin = self.__gpio.DigitalOutputDevice(
            pin = self.configuration.pin,
            active_high = self.configuration.active_high,
            initial_value = self.configuration.initial_value
        )

        self.on_high = Automation.create_automations(self, config.on_high)
        self.on_low = Automation.create_automations(self, config.on_low)


    def invoke(self, call_stack: CallStack):
        topic = call_stack.get("{{topic}}")

        call_stack = call_stack.with_keys({
            "is_active": self.output_pin.is_active
        })

        if "turn_on" == topic:
            self.output_pin.on()
            self.state.is_high = True
            for on_high in self.on_high:
                on_high.invoke(call_stack)

        if "turn_off" == topic:
            self.output_pin.off()
            self.state.is_high = False
            for on_low in self.on_low:
                on_low.invoke(call_stack)

        if "toggle" == topic:
            self.output_pin.toggle()
            if self.output_pin.is_active:
                self.state.is_high = True
                for on_high in self.on_high:
                    on_high.invoke(call_stack)
            else:
                self.state.is_high = False
                for on_low in self.on_low:
                    on_low.invoke(call_stack)

        super().invoke(call_stack)

