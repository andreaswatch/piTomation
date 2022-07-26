
# from enum import auto
# from modules.base.Configuration import *
# from modules.base.Instances import *
# import bluetooth

# @configuration
# class RfCommSensorConfiguration(SensorConfiguration):

#     @validator('platform')
#     def check_platform(cls, v):
#         platform_name = "rfcomm_server"
#         if v != platform_name:
#             raise ValueError("wrong script platform: " + platform_name + ", is: " + v)
#         return v   

#     on_message: Optional[list[AutomationConfiguration]] = [] 
#     '''List of Automations to execute when a message is received, see `modules.base.Configuration.AutomationConfiguration`'''


# class RfCommSensorState(BaseState):
#     '''Represents the last received payload'''

#     payload: Union[str, dict] = ""
#     '''Last received payload'''


# class Sensor(BaseSensor, Debuggable):
#     '''Allows to listen to a given MQTT topic.'''
#     from plugins.rfcomm_server.Platform import Platform

#     def __init__(self, parent: Platform, config: RfCommSensorConfiguration) -> None:
#         super().__init__(parent, config)
#         self.configuration = config
#         self.state = RfCommSensorState()

#         self.on_message_automations = Automation.create_automations(self, config.on_message)


#     def start(self, call_stack: CallStack):
#         pass

#     def on_message(self, call_stack: CallStack):
#         self.state.payload = call_stack.get("{{{payload}}}")
#         self.log_debug("Got payload: "+ str(self.state.payload))

#         for automation in self.on_message_automations:
#             automation.invoke(call_stack)

#         self.on_state_changed(call_stack)
