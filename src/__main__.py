import importlib
import time
from pathlib import Path
import os
import sys

def import_plugins():
    #find actual path
    realpath = os.path.realpath(__file__)
    dirname = os.path.dirname(realpath)

    #add modules & plugins
    plugin_path = os.path.join(dirname, "plugins")

    for dir_path in Path(plugin_path).rglob('*.py'):
        dp = str(dir_path)
        if dp.lower().endswith("__init__.py"):
            continue
        path = dp[len(dirname)+1:-3].replace("/",".")

        if len(path.split('.')) < 4:
            '''only import the top level plugin directory, so that potential submodules are 
            only imported if they are imported by the plugins.'''
            print(" > " + path)
            importlib.import_module(path)

print("Import plugins ..")
import_plugins()

print("Import app ..")
import modules.app.App as piTomation
app: piTomation.App 

print("Start app ..")
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
    
    

