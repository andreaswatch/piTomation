from typing import Any, List, Optional, Union
import chevron


def init_renderer():
    def __get_string(key: str, scopes, warn: bool = False):
        for scope in scopes:
            if hasattr(scope, "get_variable_value"):
                value = scope.get_variable_value(key)
                if value is not None:
                    sub_scopes = CallStack().with_stack(scopes)
                    sub_scopes.pop(0)
                    return chevron.render(value, scopes=sub_scopes)

        if key.startswith("id("):
            end = key.index(')')
            id = key[3:end]
            act = None
            for scope in scopes:
                if hasattr(scope, "get_app"):
                    act = scope.get_app().get_id(id)
                    break

            rest = key[end+2:]
            path = rest.split('.')
            return_act = False
            for path_element in path:
                if act is None:
                    return_act = False
                    break
                if hasattr(act, path_element):
                    return_act = True
                    act = getattr(act, path_element)
                elif type(act) is dict and path_element in act:
                    return_act = True
                    act = act[path_element]
                else:
                    print((type(act).__name__))
                    #return_act = False
                    break
            if return_act:
                if type(act) is str:
                    return scopes.get(act)
                return act

        result = "{{" + key + "}}"
        print(result)
        return result

    chevron.renderer._get_key = __get_string



class VariableProvider():
    def __init__(self) -> None:
        self.variables = {}
        
    def get_variable_value(self, key: str):
        key = str(key).lower()
        if key in self.variables:
            return self.variables[key]

    def __repr__(self):
        return self.variables


class CallStack(List):
    def __init__(self) -> None:
        pass


    def clone(self):
        result = CallStack()
        for item in self:
            result.append(item)
        return result


    def get_stack(self):
        stack = list(self)
        stack.reverse()
        return stack


    def with_element(self, element):
        c = self.clone()
        c.insert(0, element)
        return c


    def with_key(self, key: str, value):
        key = str(key).lower()

        class keyProvider():
            def get_variable_value(self, text: str):
                if str(text).lower() == key:
                    return value

            def __repr__(self):
                return key + "=" + value

        c = self.clone()
        c.insert(0, keyProvider())
        return c


    def with_keys(self, keys: dict):
        v = VariableProvider()
        v.variables = keys

        c = self.clone()
        c.insert(0, v)
        return c


    def with_stack(self, stack):
        i = 0
        c = self.clone()
        for item in stack:
            c.insert(i, item)
            i+=1
        return c
                

    def get(self, getKey):
        def _render(input: str):
            if not type(input) is str:
                return input

            result = chevron.render(input, scopes=self)
            return result

        return _render(getKey)
