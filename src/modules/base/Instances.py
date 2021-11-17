from ctypes import ArgumentError
from typing import Optional

from modules.base.CallStack import *
from modules.base.Configuration import *


class Base:
    """Base class for everything"""

    def __init__(self, config: Configuration) -> None:
        self.configuration = config

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__


class VariableProvider:
    def __init__(self, config: VariablesConfiguration) -> None:
        self.variables = config.variables

    def get_variable_value(self, variable_id):
        if self.variables is not None:
            if variable_id in self.variables:
                return self.variables[variable_id]


class Logging():
    """Classes that want to log should be based on this class"""

    def log_error(self, message):
        """Log an error to the console"""
        print("[ERROR] " + message)

    def log_warning(self, message):
        """Log a warning to the console"""
        print("[WARN] " + message)

    def log_info(self, message):
        """Log a info message to the console"""
        print("[INFO] " + message)        


class Debuggable():
    """Classes that want to log debug messages should be based on this class"""

    def __init__(self, config: Configuration) -> None:
        self.configuration = config

    def log_debug(self, message):
        """Log a debug message to the console (if configuration.debug == True)"""

        if hasattr(self, "configuration"):
            if hasattr(self.configuration, "debug"):
                if self.configuration.debug:
                    print("[DEBUG] " + message)


class Identifyable():
    """Base class for classes with an Identifier (id)"""

    def __init__(self, config: IdConfiguration) -> None:
        self.configuration = config

    def __str__(self):
        return super().__str__() + ": " + self.configuration.id

    def __repr__(self):
        return super().__str__() + ": " + self.configuration.id


class Disposeable():
    def __init__(self) -> None:
        self.is_disposed = False

    def dispose(self):
        self.is_disposed = True


class Stackable():
    def __init__(self, parent) -> None:

        if parent is None:
            # only for App
            return

        self.parent = parent
        self.call_stack = CallStack().with_stack(self.get_full_stack())

    def get_full_stack(self):
        scopes = self.get_parents()
        scopes.append(self)
        scopes.reverse()
        return scopes

    def get_app(self) -> 'BaseApp':
        app = self
        while (hasattr(app, "parent") and app.parent is not None):
            app = app.parent
        return app #type: ignore

    def get_parents(self) -> list['Stackable']:
        parents = []
        parent = self
        while (hasattr(parent, "parent") and parent.parent is not None):
            parent = parent.parent
            parents.insert(0, parent)
        return parents


class Device(Stackable, VariableProvider):
    def __init__(self, parent, config: DeviceConfiguration) -> None:
        Stackable.__init__(self, parent)
        VariableProvider.__init__(self, config)
        self.configuration = config
        self.variables = config.variables

        self.startup_actions = []
        if self.configuration.on_init is not None:
            for action in self.configuration.on_init:
                self.startup_actions.append(ActionTrigger(self, action))


class BaseApp(Stackable, Disposeable, VariableProvider):
    def __init__(self) -> None:
        Stackable.__init__(self, None)
        Disposeable.__init__(self)
        VariableProvider.__init__(self, VariablesConfiguration())

        self.variables = {
            "id": "piTomation"
        }

        self.device: Device
        self.platforms: list[BasePlatform]
        self.actions: list[BaseAction]
        self.sensors: list[BaseScript]


    def get_platform(self, id: str):
        '''get a configured platform by id'''
        for platform in self.platforms:
            if platform.configuration.id == id:
                return platform


    def get_id(self, id: str) -> Union['BaseScript', 'BasePlatform']:
        '''get a configured component(action/sensor/script) by id'''
        for action in self.actions:
            if action.configuration.id == id:
                return action

        for sensor in self.sensors:
            if sensor.configuration.id == id:
                return sensor

        for platform in self.platforms:
            if platform.configuration.id == id:
                return platform

        raise ArgumentError("Id " + id + " not found")


    def dispose(self):
        '''dispose all components'''

        for action in self.actions:
            action.dispose()

        for sensor in self.sensors:
            sensor.dispose()

        for platform in self.platforms:
            platform.dispose()

        super().dispose()

class BaseState():
    pass


class BaseScript(Stackable, Identifyable, Disposeable, VariableProvider):
    def __init__(self, parent: Stackable, config: ScriptConfiguration) -> None:
        Stackable.__init__(self, parent)
        Identifyable.__init__(self, config)
        Disposeable.__init__(self)
        VariableProvider.__init__(self, config)
        self.configuration = config
        self.state = BaseState

        self.variables = config.variables

        self.on_state_changed_automations = Automation\
            .create_automations(self, config.on_state_changed)        

    def start(self, call_stack: CallStack):
        '''is called when the configuration is loaded completely.
        Here is where we initialize and load stuff'''
        pass      

    def on_state_changed(self, call_stack: CallStack):
        '''must get called whenever the local state has changed'''
        for automation in self.on_state_changed_automations:
            automation.invoke(call_stack)      


class BaseSensor(BaseScript):
    def __init__(self, parent: Stackable, config: SensorConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

class BaseAction(BaseScript):
    def __init__(self, parent: Stackable, config: ActionConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

    def invoke(self, call_stack: CallStack):
        '''must get called whenever the action has been invoked'''
        self.on_state_changed(call_stack) 


class BasePlatform(Stackable, Identifyable, Disposeable):
    def __init__(self, parent: Stackable, config: PlatformConfiguration) -> None:
        Stackable.__init__(self, parent)
        Identifyable.__init__(self, config)
        Disposeable.__init__(self)

        self.configuration = config
        self.variables = config.variables

    def start(self, call_stack: CallStack):
        '''is called when the configuration is loaded completely.
        Here is where we initialize and load stuff'''
        pass


class Automation(Stackable):
    def __init__(self, parent: Stackable, config: AutomationConfiguration) -> None:
        super().__init__(parent)
        self.script = parent
        self.configuration = config

        self.__conditions = []
        if self.configuration.conditions is not None:
            for condition in self.configuration.conditions:
                self.__conditions.append(Condition(self, condition))

        self._actions = []
        if self.configuration.actions is not None:
            for action in self.configuration.actions:
                self._actions.append(ActionTrigger(self, action))

    def check_conditions(self, call_stack: CallStack):
        for condition in self.__conditions:
            if not condition.check(call_stack):
                return False
        return True

    def invoke(self, call_stack: CallStack):
        call_stack = call_stack.with_element(self)

        if not self.check_conditions(call_stack):
            return

        for action in self._actions:
            action.invoke(call_stack)

    @staticmethod
    def create_automations(parent: Stackable, conf: Optional[list[AutomationConfiguration]]):
        '''Creates automations for all given AutomationConfiguration's'''

        automations: list[Automation] = []

        if conf is not None:
            for action_conf in conf:
                automations.append(Automation(parent, action_conf))

        return automations            


class Condition(Stackable):
    def __init__(self, parent: Stackable, config: ConditionConfiguration) -> None:
        super().__init__(parent)
        self.configuration = config

    def check(self, call_stack: CallStack) -> bool:
        actual_value = call_stack.get(self.configuration.actual)
        functionName = call_stack.get(self.configuration.comperator)
        expected_value = call_stack.get(self.configuration.expected)
        invert_result = not call_stack.get(self.configuration.inverted)

        if "contains" == functionName:
            result = (expected_value in actual_value) == invert_result #type: ignore
            return result

        if "equals" == functionName:
            result = (expected_value == actual_value) == invert_result
            return result

        if "startsWith" == functionName:
            result = (actual_value.startswith(expected_value)) == invert_result #type: ignore
            return result

        if "endsWith" == functionName:
            result = (actual_value.endswith(expected_value)) == invert_result #type: ignore
            return result

        return False


class ActionTrigger(Stackable, Logging):
    def __init__(self, parent: Stackable, config: ActionTriggerConfiguration) -> None:
        Stackable.__init__(self, parent)
        Logging.__init__(self)
        self.configuration = config


    def invoke(self, call_stack: CallStack):
        app = self.get_app()
        id: BaseAction = app.get_id(self.configuration.action) #type: ignore

        if id is None:
            self.log_error("Id '" + self.configuration.action + "' not found")
            return

        call_stack = call_stack.with_element(self) 

        if self.configuration.values:
            call_stack = call_stack.with_keys(self.configuration.values)

        id.invoke(call_stack)
