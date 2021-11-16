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

