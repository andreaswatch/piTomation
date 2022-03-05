docker run -it \
  --name piTomation \
  --mount type=bind,source=/home/pi/piTomation,target=/app \
  --mount type=bind,source=/home/pi/frontdoor.yaml,target=/config.yaml \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 2200:22 \
  --device /dev/snd:/dev/snd \
  --privileged \
  awatch/pitomation:1.0.8 python \
  /app/__main__.py /config.yaml
