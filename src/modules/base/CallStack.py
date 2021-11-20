from typing import List
import chevron
import json

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
                

    def get(self, getKey, optional=False):
        def ret(key, result):
            if optional and result is None:
                #Fallback: return {{given key}} to indicate they key was not found to the user
                result = "{{" + key + "}}"
                from modules.base.Instances import Logging
                Logging.log_warning(Logging(), "Can not render key '" + key + "', returning {{" + key + "}}" )
                return key

            #try:
            #    _json = json.loads(result)
            #    return _json
            #except Exception as ex:
            #    print(ex)
            #    pass

            return result

        def _render(input: str):
            if not type(input) is str:
                return ret(input, input)

            result = chevron.render(input, scopes=self)
            return ret(input, result)

        return ret(input, _render(getKey))
