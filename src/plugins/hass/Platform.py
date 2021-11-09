from modules.app.App import VERSION
from modules.app.base.Instances import *
from plugins.hass.HassEntityAutomation import *
from plugins.hass.Configurations import *


class Platform(BasePlatform):
    def __init__(self, parent: Stackable, config: HassPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config
        self.app = parent.get_app()

        self.hass_device = self.GetDevice(parent.get_app().device)

        self.exports: list[HassEntityAutomation] = []
        for export in config.exports:
            self.exports.append(HassEntityAutomation(self, export))

    def start(self):
        self.communication = self.app.get_id(self.configuration.connection)

        super().start()

        for entity in self.exports:
            e = entity  # type: HassEntityAutomation
            e.start()

    def GetDevice(self, device: Device):
        return {
            "manufacturer": "Andreas Strauß",
            "model": "piTomation",
            "name": device.configuration.name,
            "identifiers": [device.configuration.name],
            "sw_version": "V" + str(VERSION) + "_D" + str(device.configuration.version)
        }
