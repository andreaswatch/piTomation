docker run -it --rm\
 --name piTomation \
 -v "$PWD":/home/pi/piTomation \
 -w /home/pi/ptTomation \
 arm32v6/python:3.9-alpine python\
 __main__.py
