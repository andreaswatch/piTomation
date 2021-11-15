from modules.app.App import VERSION
from modules.base.Instances import *
from plugins.hass.HassEntityAutomation import *
from plugins.hass.Configurations import *


class Platform(BasePlatform):
    '''Exports actions and sensors to HomeAssistant entities.'''

    def __init__(self, parent: Stackable, config: HassPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config
        self.app = parent.get_app()

        self.hass_device = self.get_device(parent.get_app().device)

        self.base_topic = self.configuration.base_topic
        if self.base_topic is None:
            device_name = self.app.device.configuration.name
            self.base_topic = "home/" + device_name

        self.exports: list[HassEntityAutomation] = []
        for export in config.exports:
            self.exports.append(HassEntityAutomation(self, export))


    def start(self, call_stack: CallStack):
        self.communication = self.app.get_id(self.configuration.connection)

        super().start(call_stack)

        for entity in self.exports:
            e = entity  # type: HassEntityAutomation
            e.start(call_stack)


    def get_device(self, device: Device):
        return {
            "manufacturer": "Andreas Strauss",
            "model": "piTomation",
            "name": device.configuration.name,
            "identifiers": [device.configuration.name],
            "sw_version": "piTomation-" + str(VERSION) + "_Config-" + str(device.configuration.version)
        }
