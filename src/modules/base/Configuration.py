from pydantic import BaseModel
from typing import Any, Optional, Union

from pydantic.class_validators import validator

__registry: dict[type, list[type]] = {}
'''Contains all @configuration class types, key is the base type'''

def configuration(cls):
    
    def __register(self):
        hasBase = False
        base = None
        
        for base in self.__bases__:
            hasBase = True
            if not base in __registry.keys():
                __registry[base] = []
            __registry[base].append(self)

        if not hasBase:
            if base is not None:
                if not base in __registry.keys():
                    __registry[self.Type] = []

    __register(cls)

    return cls


def WithPlugins(t: type):
    if t in __registry.keys():
        classes = list(__registry[t])
        return Union[tuple(classes)]
    return t



@configuration
class Configuration(BaseModel):
    '''Base class for all configuration classes'''

    debug: Optional[bool] = False
    '''Enable additional debugging output for this instance'''  


@configuration
class IdConfiguration(Configuration):
    '''Base class for all configuration classes that provide an Id'''

    id: str
    '''Own reference'''

@configuration
class VariablesConfiguration(Configuration):
    variables: Optional[dict]
    '''Variables, exposed as id(xy).variables.name'''


@configuration
class ConditionConfiguration(Configuration):
    actual: str
    '''Adress of the actual value, e.g. "payload"'''

    comperator: str
    '''Function name used to compare the values'''

    inverted: Optional[bool] = False
    '''Invert result'''
    
    expected: str
    '''Expected value'''


@configuration
class ActionTriggerConfiguration(Configuration):
    action: str
    '''id of the action to execute'''

    values: Optional[dict] = {}
    '''optional list of values to pass'''


@configuration
class AutomationConfiguration(Configuration):
    '''An Automation consists of optional conditions and a list of actions to execute'''

    conditions: Optional[list[ConditionConfiguration]] = []
    '''list of conditions to prove before the actions get executed'''

    actions: list[ActionTriggerConfiguration] = []
    '''list of actions to execute'''


@configuration
class StackableConfiguration(IdConfiguration, VariablesConfiguration):

    on_init: Optional[list[AutomationConfiguration]] = []
    '''Actions to execute after init is done'''

    on_dispose: Optional[list[AutomationConfiguration]] = []
    '''Actions to execute before this platform is disposed'''


@configuration
class PlatformConfiguration(StackableConfiguration):
    '''Base class for all platform configuration classes'''

    platform: str
    '''plugin name of the platform'''

    @validator('platform', always=False, allow_reuse=False)
    def check_platform_module(cls, v):
        raise ValueError("Generic PlatformConfiguration not supported for: " + v)


@configuration
class ScriptConfiguration(StackableConfiguration):
    '''Base clss for all script configuration classes'''

    platform: str
    '''The platform of this script'''

    type: Optional[str]
    '''The class type of this script'''

    on_state_changed: Optional[list[AutomationConfiguration]] = []
    '''List of Automations to execute after the sensor's state has changed'''    


@configuration
class ActionConfiguration(ScriptConfiguration):
    '''Base clss for all script configuration classes'''


@configuration
class SensorConfiguration(ScriptConfiguration):
    '''Base clas for all sensor configuration classes'''


@configuration
class DeviceConfiguration(VariablesConfiguration):
    name: str
    '''Name of the device.'''

    '''Version of the configuration'''
    version: str

    on_init: Optional[list[ActionTriggerConfiguration]] = []
    '''Actions to execute after init is done'''

