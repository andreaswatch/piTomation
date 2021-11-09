from typing import Union
import importlib
import os
import sys
from marshmallow_dataclass import class_schema
import pydantic
from pydantic.error_wrappers import ValidationError
import yaml
import json
import socket
from modules.app.base.CallStack import CallStack
from modules.app.base.Configuration import *
from modules.app.base.Instances import *

VERSION = "2021.10.26"
CONF_YAML = "yaml"
CONF_JSON = "json"
CONF = CONF_YAML


class App(BaseApp, Logging, Debuggable):
    def __init__(self) -> None:
        super().__init__()

        self.read_configuration()

        self.device = Device(self, self.configuration.device)
        self.platforms = self.init_platforms()
        self.actions = self.init_actions()
        self.sensors = self.init_sensors()

        self.log_debug("Initialization done")

        for platfrom in self.platforms:
            platfrom.start()

        self.log_debug("Platforms started")

        call_stack = CallStack(from_list=self.get_full_stack())
        for startupAction in self.device.startup_actions:
            startupAction.invoke(call_stack)


    def read_configuration(self):
        if socket.gethostname() == "DESKTOP-7CS476B":  # todo: remove
            config_filename = os.getcwd() + "/src/" + socket.gethostname() + "." + CONF
        else:
            config_filename = os.getcwd() + "/" + socket.gethostname() + "." + CONF

        if len(sys.argv) == 1:
            print("No configuration file given, use " + config_filename)
        else:
            config_filename = sys.argv[-1]

        try:
            print("Loading " + config_filename)
            with open(config_filename) as config_file:
                if (CONF == CONF_JSON):
                    raw = json.load(config_file)
                elif (CONF == CONF_YAML):
                    raw = yaml.safe_load(config_file)
                else:
                    raise Exception("Unknown config type: " + CONF)

            from marshmallow_dataclass import class_schema
            from modules.app.AppConfiguration import AppConfiguration
            #typeofactions = type(AppConfiguration())
            #print(typeofactions)
            try:
                result = AppConfiguration.parse_obj(raw)
                self.configuration = result
            except ValidationError as e:
                print(e)
                exit()

        except IOError:
            print("Configuration file not found: " + config_filename)
            exit()



    def init_platforms(self):
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

    def init_actions(self):
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

    def init_sensors(self):
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
