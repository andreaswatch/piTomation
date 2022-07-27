from enum import Enum
from modules.base.Configuration import *
from modules.base.Instances import *
from plugins.hass.Configurations import *
import json

class HassType(Enum):
    TRIGGER = "trigger"
    '''HomeAssistant's triggers are only to invoke HA Automations, not visible in Lovelace.'''

    BINARY_SENSOR = "binary_sensor"
    '''Use this type to use the state of a piTomation entity in HA.'''

    TEXT_SENSOR = "sensor"
    '''Use this type to use the state of a piTomation entity in HA.'''

    SWITCH = "switch"
    '''Allows to toggle a piTomation state from HA.'''


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

        if config.friendly_name is None:
            config.friendly_name = config.name            

        self.base_topic = str(self.platform.base_topic)
        
        self.type = HassType(config.type)

        auto_discovery_temp = str(self.type.value)

        if config.state_topic is None:
            config.state_topic = self.base_topic + "/" + config.name + "/state"
            
        if type(config) is HassActionEntityConfiguration:
            if config.command_topic is None:
                config.command_topic = self.base_topic + "/" + config.name + "/command"

            self.on_command_automations = Automation.create_automations(self, config.on_command)
            self.off_command_automations = Automation.create_automations(self, config.off_command)

        elif type(config) is HassTriggerEntityConfiguration:
            if config.command_topic is None: #type: ignore
                config.command_topic = self.base_topic + "/" + config.name + "/command"
            auto_discovery_temp = "device_automation"

        self.auto_discovery_topic = self.platform.configuration.auto_discovery_topic \
            + "/" + auto_discovery_temp \
            + "/" + self.platform.hass_device["name"] \
            + "/" + config.name \
            + "/config"
            

    def start(self, call_stack: CallStack):

        #from plugins.mqtt.Platform import Platform as mqtt_platform
        def get_mqtt_platform():# -> mqtt_platform:
            return self.platform.communication #type: ignore
        self.communication_platform = get_mqtt_platform()

        state_topic = self.base_topic + "/" + str(self.configuration.name) + "/state"
        wrapped_id = self.app.get_id(self.configuration.id)

        entity = {}
        
        entity["device"] = self.platform.hass_device

        if self.configuration.icon:
            entity["icon"] = self.configuration.icon

        def get_unique_id():
            '''Creates a unique id for HA.'''
            result = "" \
                + str(call_stack.get(self.app.device.configuration.name)) \
                + "_" \
                + str(call_stack.get(str(self.type.value))) \
                + "_" \
                + str(call_stack.get(self.configuration.id)) \
                + "_" \
                + str(call_stack.get(self.configuration.name)) 
            return result

        def get_state():
            '''Returns the internal state of the exposed entity.'''

            exp_state = str(self.configuration.expose_state) #type: ignore
            if exp_state == "OFF":
                return False
            else:
                path = exp_state.split('.') #type: ignore
                act = wrapped_id
                for path_element in path:
                    if path_element == "asJson":
                        if (len(str(act).strip()) == 0):
                            break
                        else:
                            act = json.loads(act.replace("'", '"'))    
                            print(act)

                    elif hasattr(act, path_element):
                        act = getattr(act, path_element)    
                    
                    elif type(act) is dict and path_element in act:
                        act = act[path_element]

                act_state = str(act).lower()

                if act_state == "true" or act_state == "on":
                    return entity["payload_on"]
                    
                if act_state == "false" or act_state == "off":
                    return entity["payload_off"]

                return act

        class UpdateHassState(Automation):
            '''Updates the state in HA.'''

            def invoke(_, call_stack: CallStack): #type: ignore
                act_state = get_state()
                self.communication_platform.publish(state_topic, act_state)


        wrapped_id.on_state_changed_automations.append(UpdateHassState(self, AutomationConfiguration())) #type: ignore    


        if self.type == HassType.TRIGGER and type(self.configuration) is HassTriggerEntityConfiguration:
            entity["topic"] = self.configuration.command_topic #type: ignore
            entity["automation_type"] = "trigger"
            entity["type"] = "button_short_press"
            entity["subtype"] = self.configuration.name
            
            def OnCommand(call_stack: CallStack):
                payload = call_stack.get("{{{payload}}}")

                if isinstance(wrapped_id, BaseAction):
                    '''Update local state and call the automations of the entity.'''
                    wrapped_id.invoke(call_stack)

                if payload == entity["payload_on"]:
                    if self.on_command_automations:
                        for automation in self.on_command_automations:
                            automation.invoke(call_stack)

                if payload == entity["payload_off"]:
                    if self.off_command_automations:
                        for automation in self.off_command_automations:
                            automation.invoke(call_stack)                            

            self.communication_platform.subscribe(self.configuration.command_topic, callback=OnCommand) #type: ignore
        

        elif self.type == HassType.SWITCH and type(self.configuration) is HassActionEntityConfiguration:
            entity["name"] = self.configuration.friendly_name
            entity["unique_id"] = get_unique_id()
            if self.communication_platform.configuration.availability:
                entity["availability_topic"] = call_stack.get(self.communication_platform.configuration.availability.topic)
            entity["payload_off"] = "off"
            entity["payload_on"] = "on"
            #entity["optimistic"] = False
            entity["state_topic"] = state_topic
            entity["command_topic"] = self.configuration.command_topic     
            if self.communication_platform.configuration.availability:
                entity["availability_topic"] = call_stack.get(self.communication_platform.configuration.availability.topic)
                entity["payload_available"] = call_stack.get(self.communication_platform.configuration.availability.payload_on)
                entity["payload_not_available"] = call_stack.get(self.communication_platform.configuration.availability.payload_off)                 

            def OnCommand(call_stack: CallStack):
                payload = call_stack.get("{{{payload}}}")
                boolean_payload = False
                if payload == entity["payload_on"]: 
                    boolean_payload = True
                elif payload == entity["payload_off"]: 
                    boolean_payload = False

                call_stack = call_stack.with_key("payload", boolean_payload)

                if isinstance(wrapped_id, BaseAction):
                    '''Update local state and call the automations of the entity.'''
                    wrapped_id.invoke(call_stack)

                if payload == entity["payload_on"]:
                    if self.on_command_automations:
                        for automation in self.on_command_automations:
                            automation.invoke(call_stack)

                if payload == entity["payload_off"]:
                    if self.off_command_automations:
                        for automation in self.off_command_automations:
                            automation.invoke(call_stack)                            

            self.communication_platform.subscribe(self.configuration.command_topic, callback=OnCommand) #type: ignore
        
        elif (self.type == HassType.BINARY_SENSOR or self.type == HassType.TEXT_SENSOR) and type(self.configuration) is HassBinarySensorEntityConfiguration:
            entity["name"] = self.configuration.friendly_name
            entity["unique_id"] = get_unique_id()
            entity["state_topic"] = call_stack.get(state_topic)
            entity["payload_on"] = "on"
            entity["payload_off"] = "off"
            if self.communication_platform.configuration.availability:
                entity["availability_topic"] = call_stack.get(self.communication_platform.configuration.availability.topic)
                entity["payload_available"] = call_stack.get(self.communication_platform.configuration.availability.payload_on)
                entity["payload_not_available"] = call_stack.get(self.communication_platform.configuration.availability.payload_off)                 


        if self.type == HassType.BINARY_SENSOR or self.type == HassType.TEXT_SENSOR or self.type == HassType.SWITCH:
            '''Report actual state back to HA'''
            UpdateHassState(self, AutomationConfiguration()).invoke(call_stack) 

        self.communication_platform.publish(self.auto_discovery_topic, entity, retain = True)

