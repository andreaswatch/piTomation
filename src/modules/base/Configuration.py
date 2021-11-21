'''
Basic piTomation configuration options.
'''

from pydantic import BaseModel
from typing import Any, Optional, Union

from pydantic.class_validators import validator

__pdoc__ = {
    "WithPlugins": None,
    "configuration": None
}

__registry: dict[type, list[type]] = {}
'''Contains all @configuration class types, key is the base type'''


def configuration(cls):
    '''All configurations in the configuration file must be tagged with #@configuration, so that the __registry is aware about the classes.'''
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
    '''Used internally to add all derivered types to a list'''
    if t in __registry.keys():
        classes = list(__registry[t])
        return Union[tuple(classes)]  # type: ignore
    raise Exception("AppConfiguration must get imported after all plugins")


#@configuration
class Configuration(BaseModel):
    '''Base class for all configuration classes'''

    def __init__(__pydantic_self__, **data: Any) -> None: #type: ignore
        '''YAML configuration'''
        super().__init__(**data)

    debug: Optional[bool] = False
    '''(Optional, bool): Enable additional debugging output for this instance'''

    comment: Optional[str]
    '''(Optional, string): Additional text information about this node. Not used anywhere.'''


#@configuration
class IdConfiguration(Configuration):
    '''Base class for all configuration classes that provide an Id'''

    id: str
    '''(Required, string): This is the name of the node. It should always be unique in your piTomation network.'''


#@configuration
class VariablesConfiguration(Configuration):
    '''Adds variables to an id, access: id(myId).variables.myVariable
<details>
Example:
```
platform: mqtt
variables:
 - myVariableA: "ValueA"
 - myVariableB: "On"
```
</details>    
'''

    variables: Optional[dict]
    '''(Optional, dictionary of variables): Variables, exposed as id(xy).variables.name'''


#@configuration
class ConditionConfiguration(Configuration):
    '''Configuration settings for a Condition.'''

    actual: Union[str, dict]
    '''(Required, string or dictionary): The actual value to compare, e.g. "{{payload}}".
    The value can contain either a simple string or a dictionary of values (e.g. a json payload from a mqtt message).
    '''

    comperator: str
    '''(Required, string): Function name used to compare the values, currently available: [contains, equals, startWith, endsWith].'''

    inverted: Optional[bool] = False
    '''(Optional, bool): Invert result.'''

    expected: Union[str, dict]
    '''(Required, stirng or dictionary): Expected value.'''


#@configuration
class ActionTriggerConfiguration(Configuration):
    '''Configuration settings for an ActionTrigger.
<details>
# Example 1:    
Print the last received payload to the console:
```
actions:
- action: print
  values:
    payload: "{{payload}}"
```
# Example 2:    
Print the last received topic and payload to the console:
```
actions:
- action: print
  values:
    payload: "Got a message on topic '{{topic}}' with payload: {{payload}}"
</details>
```
    '''

    action: str
    '''(Required, string): Id of the Node/Action to execute.'''

    values: Optional[dict] = {}
    '''(Optional, dictionary): Values to pass to the action.'''


class AutomationConfiguration(Configuration):
    '''An Automation consists of optional conditions and a list of actions to execute.
<details>
# Example:
If you get a payload like this:
```
{"something": "value", "type": "REGISTER_OK"}
```
and want to check if the type == "REGISTER_OK", the configuration could look like this:
```
on_...:
- conditions:
  - actual: "{{#payload}}{{type}}{{/payload}}"
    comperator: equals
    expected: REGISTER_OK
  actions:
  - action: print
    values:
      payload: Register is OK
```
If you also want to check for other values, you could add this configuration below the upper one:
```
- conditions:
  - actual: "{{#payload}}{{type}}{{/payload}}"
    comperator: equals
    expected: REGISTER_FAIL
  actions:
  - action: print
    values:
      payload: Register is FAIL
```
</details>
    '''

    conditions: Optional[list[ConditionConfiguration]] = []
    '''(Optional, list of conditions): piTomation evaluates these conditions before actions get executed, see `ConditionConfiguration`.'''

    actions: list[ActionTriggerConfiguration] = []
    '''(Required, list of actions): Actions to execute, see `ActionTriggerConfiguration`.'''


class StackableConfiguration(IdConfiguration, VariablesConfiguration):
    '''Provides default Automations that are executed by all Platforms, Actions and Sensors'''

    on_init: Optional[list[AutomationConfiguration]] = []
    '''(Optional, List of Automations): Automations to execute after init is done, see `AutomationConfiguration`.'''

    on_dispose: Optional[list[AutomationConfiguration]] = []
    '''(Optional, List of Automations): Automations to execute before this platform is disposed, see `AutomationConfiguration`.'''


class PlatformConfiguration(StackableConfiguration):
    '''Base class for all platform configuration classes'''

    platform: str
    '''(Required, string): Plugin name of the platform.'''


class ScriptConfiguration(StackableConfiguration):
    '''Base clss for all script configuration classes.'''

    platform: str
    '''(Required, string): The platform of this script.'''

    type: Optional[str]
    '''(Optional, string): The class type of this script.'''

    on_state_changed: Optional[list[AutomationConfiguration]] = []
    '''(Optional, List of Automations): Automations to execute after the Sensor's state has changed, see `AutomationConfiguration`.'''


class ActionConfiguration(ScriptConfiguration):
    '''Base class for all script configuration classes.'''


class SensorConfiguration(ScriptConfiguration):
    '''Base clas for all sensor configuration classes'''

class DeviceConfiguration(VariablesConfiguration):
    name: str
    '''(Required, string): Name of the device.'''

    version: str
    '''(Required, string): Version of the configuration.'''

    on_init: Optional[list[ActionTriggerConfiguration]] = []
    '''(Optional, List of Actions): Actions to execute after init is done, see `ActionTriggerConfiguration`.'''
