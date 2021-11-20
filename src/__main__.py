import importlib
import time
import modules.app.App as piTomation
from pathlib import Path

app: piTomation.App

def import_plugins():
    plugin_path = "./src/plugins/"

    for path in Path(plugin_path).rglob('*.py'):
        plugin = ""
        for l in path.parts[1:-1]:
            plugin += "." + l
        path = str.join(".", path.parts[1:-1]) + "." + path.parts[-1].replace(".py","")

        if path.endswith("__init__"):
            continue

        if len(path.split('.')) < 4:
            '''only import the top level plugin directory, so that potential submodules are 
            only imported if they are imported by the plugins.'''
            importlib.import_module(path)

import_plugins()

app = piTomation.App()

#try:
#    app = piTomation.App()
#except Exception as ex:
#    print(ex)
#    exit()

try:
    while not app.is_disposed:
        time.sleep(1)

except Exception as ex:
    print(ex)
    
    

