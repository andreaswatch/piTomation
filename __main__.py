import sys, os

#find actual path
realpath = os.path.realpath(__file__)
dirname = os.path.dirname(realpath)

#add modules & plugins
app_path = os.path.join(dirname, "src")
sys.path.append(app_path)

#start app
from src import __main__ as main
main()