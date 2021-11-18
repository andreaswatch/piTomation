from enum import Enum
from colorzero import Color
from plugins.gpio.Platform import Platform
from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class RgbLedConfiguration(ActionConfiguration):
    '''Configuration settings for a RGB LED'''

    pin_red: str
    '''GPIO PIN name for the red led. e.g. GPIO22'''

    pin_green: str
    '''GPIO PIN name for the green led. e.g. GPIO22'''

    pin_blue: str
    '''GPIO PIN name for the blue led. e.g. GPIO22'''

    on_high: list[AutomationConfiguration] = []
    '''List of Automations to execute when the LED is turned on, see `modules.base.Configuration.AutomationConfiguration`'''

    on_low: list[AutomationConfiguration] = []
    '''List of Automations to execute when the LED is turned on, see `modules.base.Configuration.AutomationConfiguration`'''

    on_color_changed: list[AutomationConfiguration] = []
    '''List of Automations to execute when the LED's color has changed, see `modules.base.Configuration.AutomationConfiguration`'''

    active_high: bool = True
    '''True=normal, False=inverted'''

    initial_color: str = "black"
    '''Initial Color (see colorzero)'''

    pwm: bool = False
    '''enable PWM for the led'''

    @validator('platform')
    def __check_platform(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class RbgLedState(BaseState):
    '''Represents the state of the LED'''

    color: str 
    '''Returns the actual configured color of the LED'''

    is_active: bool
    '''Returns if the LED is on(True) or off(False)'''


class RgbLedCommands(Enum):
    '''Available commands to control the LED'''

    on = "on"
    '''Turn the LED on'''

    off = "off"
    '''Turn the LED off'''

    toggle = "toggle"
    '''Toggle on/off'''

    set_color = "set_color"
    '''Change the color of the led, use payload needs to contain a color (red/green/yellow/..)'''


class RgbLed(BaseAction, Debuggable, Logging):
    '''Control the state of a RGB led'''

    def __init__(self, platform: Platform, config: RgbLedConfiguration) -> None:
        super().__init__(platform, config)

        self.gpio = platform.gpio
        self.configuration = config
        self.state = RbgLedState()

        self.led = self.gpio.RGBLED(
            red = self.configuration.pin_red,
            green = self.configuration.pin_green,
            blue = self.configuration.pin_blue,
            active_high = self.configuration.active_high,
            pwm = self.configuration.pwm,
            initial_value = Color(self.configuration.initial_color)
        )

        self.state.is_active = self.led.is_active
        self.state.color = self.led.color.html

        self.on_high = Automation.create_automations(self, self.configuration.on_high)
        self.on_low = Automation.create_automations(self, self.configuration.on_low)
        self.on_color_changed = Automation.create_automations(self, self.configuration.on_color_changed)


    def invoke(self, call_stack: CallStack):
        topic = str(call_stack.get("{{topic}}"))
        self.log_debug("Command: " + topic)

        call_stack = call_stack.with_element(self)
        last_state = self.led.is_active

        self.log_debug(str(topic))

        if RgbLedCommands.toggle.name == topic:
            self.led.toggle()
            self.state.color = self.led.color.html
            self.state.is_active = self.led.is_active
            if not last_state == self.led.is_active:                
                if self.led.is_active:
                    for automation in self.on_high:
                        automation.invoke(call_stack)
                else:
                    for automation in self.on_low:
                        automation.invoke(call_stack)            

        elif RgbLedCommands.on.name == topic:
            self.led.on()
            self.state.color = self.led.color.html
            self.state.is_active = self.led.is_active            
            for automation in self.on_high:
                automation.invoke(call_stack)

        elif RgbLedCommands.off.name == topic:
            self.led.off()
            self.state.color = self.led.color.html
            self.state.is_active = self.led.is_active            
            for automation in self.on_low:
                automation.invoke(call_stack)

        elif RgbLedCommands.set_color.name == topic:
            payload = call_stack.get("{{payload}}")
            self.led.color = Color(payload)
            self.state.color = self.led.color.html
            self.state.is_active = self.led.is_active            
            for automation in self.on_color_changed:
                automation.invoke(call_stack)

        else:
            self.log_error("Unknown command: {{" + topic + "}}")

        self.state.is_active = self.led.is_active

        super().invoke(call_stack)

