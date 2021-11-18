import importlib
import os
import sys
from pydantic.error_wrappers import ValidationError
import yaml
import json
import socket
from modules.base.CallStack import CallStack
from modules.base.Configuration import *
from modules.base.Instances import *
from modules.base.chevron_renderer import *

VERSION = "2021.11.18"

class App(BaseApp, Logging, Debuggable):
    def __init__(self) -> None:
        '''
        Based on: `src.modules.base.Instances.BaseApp`
        '''
        super().__init__()

        init_renderer(self)

        self.__read_configuration()

        self.device = Device(self, self.configuration.device)
        self.platforms = self.__init_platforms()
        self.actions = self.__init_actions()
        self.sensors = self.__init_sensors()

        self.log_debug("Initialization done")

        call_stack = CallStack().with_stack(self.get_full_stack())

        for platfrom in self.platforms:
            platfrom.start(call_stack)

        for action in self.actions:
            action.start(call_stack)

        for sensor in self.sensors:
            sensor.start(call_stack)

        self.log_debug("Platforms started")

        for startupAction in self.device.startup_actions:
            startupAction.invoke(call_stack)


    def get_id(self, id: str):
        '''get a configured component(action/sensor/script +app&device) by id'''

        if id == "device":
            return self.device

        if id == "app":
            return self

        return super().get_id(id)


    def __read_configuration(self):
        '''Read the configuration file'''
        '''If the filename is not given in cli args, try to find the config file by the device's hostname.'''

        config_filename = ""
        if len(sys.argv) == 0:
            config_filename = os.getcwd() + "/" + socket.gethostname() + ".yaml"
            self.log_info("No configuration file given, fallback to '" + config_filename + "'")
        else:
            config_filename = sys.argv[-1]

        try:
            self.log_debug("Loading '" + config_filename + "'")
            with open(config_filename) as config_file:
                if config_filename.upper().endswith(".YAML"):
                    raw = yaml.safe_load(config_file)
                elif config_filename.upper().endswith(".YAML"):
                    raw = json.load(config_file)
                else:
                    self.log_error("Unknown config type: " + config_filename)
                    exit()

            from modules.app.AppConfiguration import AppConfiguration

            try:
                result = AppConfiguration.parse_obj(raw)
                self.configuration = result

            except ValidationError as e:
                print(e)
                exit()

        except IOError:
            print("Configuration file not found: " + config_filename)
            exit()


    def __init_platforms(self):
        result: list[BasePlatform] = []
        if self.configuration.platforms is not None:
            for platform_conf in self.configuration.platforms:
                platform_conf: PlatformConfiguration = platform_conf
                module_name = platform_conf.platform + ".Platform"
                module = importlib.import_module(module_name)
                class_name = "Platform"
                ctor = getattr(module, class_name)
                result.append(ctor(self, platform_conf))
        return result


    def __init_actions(self):
        result: list[BaseAction] = []
        if self.configuration.actions is not None:
            for action_conf in self.configuration.actions:
                action_conf: ScriptConfiguration = action_conf
                module_name = "plugins." + action_conf.platform
                class_name = "Action"
                if action_conf.type is not None:
                    class_name = action_conf.type
                module_name += "." + class_name
                module = importlib.import_module(module_name)
                ctor = getattr(module, class_name)
                platform = self.get_platform(action_conf.platform)
                result.append(ctor(platform, action_conf))
        return result


    def __init_sensors(self):
        result: list[BaseScript] = []
        if self.configuration.sensors is not None:
            for sensor_conf in self.configuration.sensors:
                sensor_conf: ScriptConfiguration = sensor_conf
                module_name = "plugins." + sensor_conf.platform
                class_name = "Sensor"
                if sensor_conf.type is not None:
                    class_name = sensor_conf.type
                module_name += "." + class_name
                module = importlib.import_module(module_name)
                ctor = getattr(module, class_name)
                platform = self.get_platform(sensor_conf.platform)
                result.append(ctor(platform, sensor_conf))
        return result
