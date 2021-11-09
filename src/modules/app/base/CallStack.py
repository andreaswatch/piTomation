from typing import Any, Optional, Union
import chevron

from modules.app.base.Configuration import PlatformConfiguration, ScriptConfiguration

def init_renderer():
    def __get_string(key: str, scopes: list[Any], warn: bool = False):
        for scope in scopes:
            if hasattr(scope, "get_variable_value"):
                value = scope.get_variable_value(key)
                if value is not None:
                    return value

        if key.startswith("id("):
            end = key.index(')')
            id = key[3:end]
            act = None
            for scope in scopes:
                if hasattr(scope, "get_app"):
                    act = scope.get_app().get_id(id)
                    break
            rest = key[end+1:]
            path = rest.split('.')
            return_act = False
            for path_element in path:
                if act is None:
                    return_act = False
                    break
                if hasattr(act, path_element):
                    return_act = True
                    act = getattr(act, path_element)
            if return_act:
                return act

        result = "{{" + key + "}}"
        print(result)
        return result

    chevron.renderer._get_key = __get_string

init_renderer()


class CallStack:
    def __init__(self, item: Any = None, from_list: Union[None, list[Any]] = None) -> None:
        if from_list is None:
            self.__stack = []
        else:
            self.__stack = list(from_list)
        pass
        if item is not None:
            self.__stack.append(item)

    def get_stack(self):
        stack = list(self.__stack)
        stack.reverse()
        return stack

    def with_(self, item):
        return CallStack(from_list=self.__stack, item=item)

    def with_key(self, key: str, value):
        key = str(key).lower()

        class keyProvider():
            def get_variable_value(self, text: str):
                if str(text).lower() == key:
                    return value

            def __repr__(self):
                return key + "=" + value

        return CallStack(from_list=self.__stack, item=keyProvider())

    def with_keys(self, dict):
        class dictKeyProvider():
            def get_variable_value(self, key: str):
                key = str(key).lower()
                if key in dict:
                    return dict[key]

            def __repr__(self):
                return dict

        return CallStack(from_list=self.__stack, item=dictKeyProvider())

    def get(self, getKey):
        def Render(renderText: str):
            if not type(renderText) is str:
                return renderText
            result = chevron.render(renderText, scopes=self.get_stack())
            return result

        for item in self.get_stack():
            if hasattr(item, "get_variable_value"):
                value = item.get_variable_value(getKey)
                if type(value) == str:
                    return Render(value)

        return Render(getKey)
