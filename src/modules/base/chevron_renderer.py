import chevron
from modules.base.CallStack import CallStack
from modules.base.Instances import Logging


def init_renderer(app):
    '''Initialize the chevron renderer'''

    __logger = Logging()

    def __get_string(key: str, scopes, warn: bool = False):

        for scope in scopes:
            #walk up the scopes, try to get the desired key and return if found
            if hasattr(scope, "get_variable_value"):
                value = scope.get_variable_value(key)
                if value is not None:
                    sub_scopes = CallStack().with_stack(scopes)
                    sub_scopes.pop(0)
                    return chevron.render(value, scopes=sub_scopes)

        if key.startswith("id("):
            #Special mode, e.g. id(**).field.subfield allows to access the instances directly.
            #The concept is to find the id in the app and then follow the path (splitted by .) until the last element.
            end = key.index(')')
            id = key[3:end]
            act = app.get_id(id)
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
                    break
            if return_act:
                if type(act) is str:
                    return scopes.get(act)
                return act

        #Fallback: return {{given key}} to indicate they key was not found to the user
        result = "{{" + key + "}}"
        __logger.log_warning("Can not render key '" + key + "', returning {{" + key + "}}" )
        return result

    chevron.renderer._get_key = __get_string
