from typing import Optional
from modules.app.base.CallStack import CallStack
from modules.app.base.Configuration import *


class Base:
    """Base class for everything"""
    def __init__(self, config: Configuration) -> None:
        self.configuration = config  

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__


class Logging():
    """Classes that want to log should be based on this class"""

    def log_error(self, message):
        """Log an error to the console"""
        print("[ERROR] " + message)


    def log_warning(self, message):
        """Log a warning to the console"""
        print("[WARN] " + message) 


class Debuggable():
    """Classes that want to log debug messages should be based on this class"""

    def __init__(self, config: Configuration) -> None:
        self.configuration = config

    def log_debug(self, message):
        """Log a debug message to the console (if configuration.debug == True)"""

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


class VariableProvider():
    def __init__(self, config: VariableConfiguration) -> None:
        self.configuration = config

        self.variables = {}


    def get_variable_value(self, name: str) -> Optional[str]:
        name = str(name).lower()
        if hasattr(self.configuration, "variables"):
            if self.configuration.variables is not None:
                return self.configuration.variables.get(name)


class Stackable():
    def __init__(self, parent) -> None:

        if parent is None:
            # only for App
            return

        self.parent = parent
        self.call_stack = CallStack(from_list=self.get_full_stack())


    def get_full_stack(self):
        scopes = self.get_parents()
        scopes.append(self)
        scopes.reverse()
        return scopes


    def get_app(self) -> 'BaseApp':
        app = self
        while (hasattr(app, "parent") and app.parent is not None):
            app = app.parent
        return app #types: BaseApp


    def get_parents(self) -> list['Stackable']:
        parents = []
        parent = self
        while (hasattr(parent, "parent") and parent.parent is not None):
            parent = parent.parent
            parents.insert(0, parent)
        return parents
    

class Device(VariableProvider, Stackable):
    def __init__(self, parent, config: DeviceConfiguration) -> None:
        super().__init__(parent)
        self.configuration = config

        self.startup_actions = []
        if self.configuration.on_init is not None:
            for action in self.configuration.on_init:
                self.startup_actions.append(ActionTrigger(self, action))


class BaseApp(VariableProvider, Stackable, Disposeable):
    def __init__(self) -> None:
        super().__init__(VariableConfiguration())
        
        self.id = "piTomation"
        self.is_disposed = False

        self.device: Device
        self.platforms: list[BasePlatform]
        self.actions: list[BaseAction]
        self.sensors: list[BaseScript]

        self.variables["name"] = "piTomation"

    def get_platform(self, id: str):
        for platform in self.platforms:
            if platform.configuration.id == id:
                return platform

    def get_id(self, id: str) -> Union['BaseAction', 'BaseScript', 'BasePlatform', None]:
        for action in self.actions:
            if action.configuration.id == id:
                return action

        for sensor in self.sensors:
            if sensor.configuration.id == id:
                return sensor

        for platform in self.platforms:
            if platform.configuration.id == id:
                return platform

        return None


    def dispose(self):
        for action in self.actions:
            action.dispose()

        for sensor in self.sensors:
            sensor.dispose()

        for platform in self.platforms:
            platform.dispose()

        super().dispose()


class BaseScript(Stackable, Identifyable, Disposeable):
    def __init__(self, parent: Stackable, config: ScriptConfiguration) -> None:
        super().__init__(parent)
        self.configuration = config

    def _create_automations(self, conf: Optional[list[AutomationConfiguration]]):
        '''Creates automations for all given AutomationConfiguration's'''

        automations: list[Automation] = []

        if conf is not None:
            for action_conf in conf:
                automations.append(Automation(self, action_conf))
            
        return automations          
        

class BaseSensor(BaseScript):
    def __init__(self, parent: Stackable, config: SensorConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

        self.on_state_changed_automations = self._create_automations(config.on_state_changed)

    def on_state_changed(self, call_stack: CallStack):
        '''must get called whenever the local state has changed'''
        for automation in self.on_state_changed_automations:
            automation.invoke(call_stack)


class BaseAction(BaseScript):
    def __init__(self, parent: Stackable, config: ActionConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

        self.on_invoked_automations = self._create_automations(config.on_invoked)

    def invoke(self, call_stack: CallStack):
        '''must get called whenever the action has been invoked'''
        for automation in self.on_invoked_automations:
            automation.invoke(call_stack)
        


class BasePlatform(Stackable, Identifyable, Disposeable, VariableProvider):
    def __init__(self, parent: Stackable, config: PlatformConfiguration) -> None:
        super().__init__(parent)
        self.configuration = config

    def start(self):
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

        self.__actions = []
        if self.configuration.actions is not None:
            for action in self.configuration.actions:
                self.__actions.append(ActionTrigger(self, action))


    def check_conditions(self, call_stack: CallStack):
        for condition in self.__conditions:
            if not condition.check(call_stack):
                return False
        return True


    def invoke(self, call_stack: CallStack):
        call_stack = call_stack.with_(self)

        if not self.check_conditions(call_stack):
            return

        for action in self.__actions:
            action.invoke(call_stack)


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
            result = (expected_value in actual_value) == invert_result
            return result

        if "equals" == functionName:
            result = (expected_value == actual_value) == invert_result
            return result

        if "startsWith" == functionName:
            result = (actual_value.startswith(expected_value)) == invert_result
            return result

        if "endsWith" == functionName:
            result = (actual_value.endswith(expected_value)) == invert_result
            return result

        return False


class ActionTrigger(Stackable, Logging):
    def __init__(self, parent: Stackable, config: ActionTriggerConfiguration) -> None:
        super().__init__(parent)
        self.configuration = config

    def render(self, call_stack: CallStack, values: Union[None,dict]):
        if values is None:
            return 
        values = dict(values)

        for item in values.keys():
            if type(values[item]) is dict:
                self.render(call_stack, item)
            else:
                values[item] = call_stack.get(values[item])

        return values


    def invoke(self, call_stack: CallStack):
        app = self.get_app()
        id: BaseAction = app.get_id(self.configuration.action)

        if id is None:
            self.log_error("Id '" + self.configuration.action + "' not found")
            return

        rendered = self.render(call_stack, self.configuration.values)

        call_stack = call_stack.with_(self) \
            .with_keys(rendered)

        id.invoke(call_stack)
