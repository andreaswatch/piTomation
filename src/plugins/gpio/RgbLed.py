from enum import auto
from colorzero import Color
from plugins.gpio.Platform import Platform
from modules.base.Configuration import *
from modules.base.Instances import *


@configuration
class RgbLedConfiguration(ActionConfiguration):
    '''Action to control the color of a RGB Led, use {{topic}} to invoke
    actions like on, off or toggle.
    To change the color, call:
    values:
      topic: set_color
      payload: green
    '''

    pin_red: str
    '''GPIO PIN name for the red led. e.g. GPIO22'''

    pin_green: str
    '''GPIO PIN name for the green led. e.g. GPIO22'''

    pin_blue: str
    '''GPIO PIN name for the blue led. e.g. GPIO22'''

    on_high: list[AutomationConfiguration] = []
    '''list actions to to execute when the LED is turned on'''

    on_low: list[AutomationConfiguration] = []
    '''list actions to to execute when the LED is turned on'''

    on_color_changed: list[AutomationConfiguration] = []
    '''list actions to to execute when the LED's color has changed'''

    active_high: bool = True
    '''True=normal, False=inverted'''

    initial_color: str = "black"
    '''Initial Color (see colorzero)'''

    pwm: bool = False
    '''enable PWM for the led'''

    @validator('platform')
    def check_platform_module(cls, v):
        platform_name = "gpio"
        if v != platform_name:
            raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
        return v    


class RgbLed(BaseAction, Debuggable):
    '''Control the state of a RGB led'''

    def __init__(self, platform: Platform, config: RgbLedConfiguration) -> None:
        super().__init__(platform, config)
        self.GPIO = platform.GPIO
        self.configuration = config

        self.Led = self.GPIO.RGBLED(
            red = self.configuration.pin_red,
            green = self.configuration.pin_green,
            blue = self.configuration.pin_blue,
            active_high = self.configuration.active_high,
            pwm = self.configuration.pwm,
            initial_value = Color(self.configuration.initial_color)
        )

        self.on_high = self._create_automations(self.configuration.on_high)
        self.on_low = self._create_automations(self.configuration.on_low)
        self.on_color_changed = self._create_automations(self.configuration.on_color_changed)


    def invoke(self, call_stack: CallStack):
        topic = call_stack.get("topic")

        last_state = self.Led.is_active

        call_stack = call_stack.with_keys({
            "is_active": self.Led.is_active,
            "color": self.Led.color
            })

        self.log_debug(str(topic))

        if "toggle" == topic:
            self.Led.toggle()
            if not last_state == self.Led.is_active:
                if self.Led.is_active:
                    for automation in self.on_high:
                        automation.invoke(call_stack)
                else:
                    for automation in self.on_low:
                        automation.invoke(call_stack)            

        if "on" == topic:
            self.Led.on()
            for automation in self.on_high:
                automation.invoke(call_stack)

        if "off" == topic:
            self.Led.off()
            for automation in self.on_low:
                automation.invoke(call_stack)

        if "set_color" == topic:
            payload = call_stack.get("payload")
            self.Led.color = Color(payload)
            for automation in self.on_color_changed:
                automation.invoke(call_stack)

        super().invoke(call_stack)
