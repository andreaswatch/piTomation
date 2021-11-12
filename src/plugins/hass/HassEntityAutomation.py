from enum import Enum
from pydantic.main import BaseModel
from modules.app.base.Configuration import *
from modules.app.base.Instances import *
from plugins.hass.Configurations import *

class HassType(Enum):
    TRIGGER = "trigger"
    SENSOR = "binary_sensor"
    ACTION = "switch"


class HassEntityAutomation(Stackable, Disposeable):

    def __init__(self, parent: Stackable, config: HassEntityConfiguration) -> None:
        from plugins.hass.Platform import Platform
        super().__init__(parent)
        
        self.platform: Platform = parent 
        self.configuration = config
        self.app = parent.get_app()
        
        if config.name is None:
            config.name = config.id
        
        self.hass_type = HassType.SENSOR

        if (config is HassBinarySensorEntityConfiguration):
            self.hass_type = HassType.SENSOR
            c: HassBinarySensorEntityConfiguration = config
            if c.state_topic is None:
                c.state_topic = self.platform.configuration.base_topic + "/" + c.id + "/state"
            
        elif config is HassActionEntityConfiguration:
            self.hass_type = HassType.ACTION
            c: HassActionEntityConfiguration = config
            if c.state_topic is None:
                c.state_topic = self.platform.configuration.base_topic + "/" + c.id + "/state"
            if c.command_topic is None:
                c.command_topic = self.platform.configuration.base_topic + "/" + c.id + "/command"

        elif config is HassTriggerEntityConfiguration:
            self.hass_type = HassType.TRIGGER
            c: HassActionEntityConfiguration = config
            if c.command_topic is None:
                c.command_topic = self.platform.configuration.base_topic + "/" + c.id + "/command"
            
        self.auto_discovery_topic = self.platform.configuration.auto_discovery_topic \
            + "/" + str(self.hass_type) \
            + "/" + self.platform.hass_device["name"] \
            + "/" + config.id \
            + "/config"


    def start(self, call_stack: CallStack):
        from plugins.mqtt.Platform import Platform as mqtt_platform
        self.mqtt: mqtt_platform = self.platform.communication

        class UpdateHass():
            def invoke(_, call_stack: CallStack):
                self.mqtt.Publish(self.configuration.state_topic, call_stack.get("payload"))

        wrapped_id = self.app.get_id(self.configuration.id)

        if wrapped_id is BaseSensor:
            w: BaseSensor = wrapped_id
            w.on_state_changed_automations.append(UpdateHass())
        elif wrapped_id is BaseAction:
            w: BaseAction = wrapped_id
            w.on_invoked_automations.append(UpdateHass())

        entity = {}
        entity["device"] = self.platform.hass_device
        entity["name"] = self.configuration.id
        entity["friendly_name"] = self.configuration.name

        if self.hass_type == HassType.TRIGGER:
            entity["topic"] = self.configuration.command_topic
            entity["type"] = "button_short_press"
            entity["subtype"] = self.configuration.id

        elif self.hass_type == HassType.ACTION:
            entity["unique_id"] = self.app.device.configuration.name \
                + "_" + str(self.hass_type) + "_" + self.configuration.id
            entity["availability_topic"] = self.mqtt.configuration.availability.topic
            entity["state_topic"] = self.configuration.state_topic
            entity["command_topic"] = self.configuration.command_topic
            entity["payload_off"] = "off"
            entity["payload_on"] = "on"
            entity["optimistic"] = False

            def OnCommand(call_stack: CallStack):
                id = self.app.get_id(self.configuration.id)
                id.invoke(call_stack)
            
            self.mqtt.subscribe(self.configuration.command_topic, callback=OnCommand)
        
        elif self.hass_type == HassType.SENSOR:
            entity["unique_id"] = self.app.device.configuration.name \
                + "_" + str(self.hass_type) + "_" + self.configuration.id
            entity["availability_topic"] = self.mqtt.configuration.availability.topic
            entity["state_topic"] = self.configuration.state_topic
            entity["payload_off"] = "off"
            entity["payload_on"] = "on"

        self.mqtt.publish(self.auto_discovery_topic, entity)

