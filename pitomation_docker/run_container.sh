# --name piTomation \

#docker run -it \
# -v "$PWD":/home/pi/piTomation \
# --mount type=bind,source="$(pwd)"/../,target=/app \
# --mount type=bind,source="$(pwd)"/home/pi/piTomation/src/frontdoor.yaml,target=/app/config.yaml \
# -w /home/pi/piTomation awatch/pitomation:1.0.2 python\
# /app/__main__.py /app/config.yaml

docker run -it \
  --mount type=bind,source=/home/pi/piTomation,target=/app \
  --mount type=bind,source=/home/pi/frontdoor.yaml,target=/config.yaml \
  --device /dev/snd:/dev/snd \
  --privileged \
  awatch/pitomation:1.0.3 python \
  /app/__main__.py /config.yaml
