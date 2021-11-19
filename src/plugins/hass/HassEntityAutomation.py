from enum import Enum
from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.hass.Configurations import *

class HassType(Enum):
    TRIGGER = "trigger"
    SENSOR = "binary_sensor"
    ACTION = "switch"


class HassEntityAutomation(Stackable, Disposeable, Logging):
    '''Connection between our actions and scripts and HomeAssistants different entity types.'''

    def __init__(self, parent: Stackable, config: HassEntityConfiguration) -> None:
        from plugins.hass.Platform import Platform
        super().__init__(parent)
        
        self.platform: Platform 
        if type(parent) is Platform:
            self.platform = parent 

        self.configuration = config
        self.app = parent.get_app()
        
        if config.name is None:
            config.name = config.id

        self.base_topic = str(self.platform.base_topic)
        
        self.hass_type = HassType.SENSOR

        if type(config) is HassBinarySensorEntityConfiguration:
            self.hass_type = HassType.SENSOR
            if config.state_topic is None:
                config.state_topic = self.base_topic + "/" + config.id + "/state"
            
        elif type(config) is HassActionEntityConfiguration:
            self.hass_type = HassType.ACTION
            if config.state_topic is None:
                config.state_topic = self.base_topic + "/" + config.id + "/state"
            if config.command_topic is None:
                config.command_topic = self.base_topic + "/" + config.id + "/command"

            self.on_command_automations = Automation.create_automations(self, config.on_command)
            self.off_command_automations = Automation.create_automations(self, config.off_command)

        elif type(config) is HassTriggerEntityConfiguration:
            self.hass_type = HassType.TRIGGER
            if config.command_topic is None: #type: ignore
                config.command_topic = self.base_topic + "/" + config.id + "/command"
            
        self.auto_discovery_topic = self.platform.configuration.auto_discovery_topic \
            + "/" + str(self.hass_type.value) \
            + "/" + self.platform.hass_device["name"] \
            + "/" + config.id \
            + "/config"


    def start(self, call_stack: CallStack):

        from plugins.mqtt.Platform import Platform as mqtt_platform
        def get_mqtt_platform() -> mqtt_platform:
            return self.platform.communication #type: ignore
        self.mqtt = get_mqtt_platform()

        state_topic = self.base_topic + "/" + self.configuration.id + "/state"
        wrapped_id = self.app.get_id(self.configuration.id)

        entity = {}
        
        entity["device"] = self.platform.hass_device
        entity["name"] = self.configuration.id

        if self.configuration.icon:
            entity["icon"] = self.configuration.icon

        def get_unique_id():
            return "" \
                + str(call_stack.get(self.app.device.configuration.name)) \
                + "_" \
                + str(call_stack.get(str(self.hass_type.value))) \
                + "_" \
                + str(call_stack.get(self.configuration.id))


        if self.mqtt.configuration.availability:
            entity["availability_topic"] = call_stack.get(self.mqtt.configuration.availability.topic)
            entity["payload_available"] = call_stack.get(self.mqtt.configuration.availability.payload_on)
            entity["payload_not_available"] = call_stack.get(self.mqtt.configuration.availability.payload_off)        


        if self.hass_type == HassType.TRIGGER and type(self.configuration) is HassTriggerEntityConfiguration:
            entity["topic"] = self.configuration.command_topic #type: ignore
            entity["type"] = "button_short_press"
            entity["subtype"] = self.configuration.id
            entity["command_topic"] = self.configuration.command_topic            
            
            def OnCommand(call_stack: CallStack):
                payload = call_stack.get("{{payload}}")
                if payload == entity["payload_on"]:
                    if self.on_command_automations:
                        for automation in self.on_command_automations:
                            automation.invoke(call_stack)

                if payload == entity["payload_off"]:
                    if self.off_command_automations:
                        for automation in self.off_command_automations:
                            automation.invoke(call_stack)                            

            self.mqtt.subscribe(self.configuration.command_topic, callback=OnCommand) #type: ignore
        

        elif self.hass_type == HassType.ACTION and type(self.configuration) is HassActionEntityConfiguration:
            entity["unique_id"] = get_unique_id()
            if self.mqtt.configuration.availability:
                entity["availability_topic"] = call_stack.get(self.mqtt.configuration.availability.topic)
            entity["payload_off"] = "on"
            entity["payload_on"] = "off"
            entity["optimistic"] = False
            entity["state_topic"] = state_topic
            entity["command_topic"] = self.configuration.command_topic            

            def OnCommand(call_stack: CallStack):
                payload = call_stack.get("{{payload}}")
                if payload == entity["payload_on"]:
                    if self.on_command_automations:
                        for automation in self.on_command_automations:
                            automation.invoke(call_stack)

                if payload == entity["payload_off"]:
                    if self.off_command_automations:
                        for automation in self.off_command_automations:
                            automation.invoke(call_stack)                            

            self.mqtt.subscribe(self.configuration.command_topic, callback=OnCommand) #type: ignore
        
        elif self.hass_type == HassType.SENSOR and type(self.configuration) is HassBinarySensorEntityConfiguration:
            entity["unique_id"] = get_unique_id()
            entity["state_topic"] = call_stack.get(state_topic)
            entity["payload_on"] = "on"
            entity["payload_off"] = "off"


        def get_state():
            path = str(self.configuration.expose_state).split('.') #type: ignore
            act = wrapped_id
            for path_element in path:
                act = getattr(act, path_element)
            return act

        if self.hass_type == HassType.SENSOR or self.hass_type == HassType.ACTION:
            class UpdateHassState(Automation):
                def invoke(_, call_stack: CallStack): #type: ignore
                    act_state = get_state()
                    if act_state:
                        self.mqtt.publish(state_topic, entity["payload_on"])
                    else:
                        self.mqtt.publish(state_topic, entity["payload_off"])

            wrapped_id.on_state_changed_automations.append(UpdateHassState(self, AutomationConfiguration())) #type: ignore    

            UpdateHassState(self, AutomationConfiguration()).invoke(call_stack)         

        self.mqtt.publish(self.auto_discovery_topic, entity, retain = True)

