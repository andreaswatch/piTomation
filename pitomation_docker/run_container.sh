# --name piTomation \
docker run -it \
 -v "$PWD":/home/pi/piTomation \
 --mount type=bind,source="$(pwd)"/../,target=/app \
 --mount type=bind,source="$(pwd)"/home/pi/frontdoor.yaml,target=/app/config.yaml \
 -w /home/pi/piTomation awatch/pitomation:1.0.2 python\
 /app/__main__.py /app/config.yaml
