docker run -it \
  --name piTomationHome \
  --mount type=bind,source=/data/automations/piTomation,target=/app \
  --mount type=bind,source=/home/pi/piTomation_home.yaml,target=/config.yaml \
  --mount type=bind,source=/mnt/BigOne/SmartHome/Cam/FrontdoorImages,target=/var/lib/www \
  --mount type=bind,source=/data/data/ssl,target=/ssl \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 2200:22 \
  -p 8301:8301 \
  --device /dev/snd:/dev/snd \
  --privileged \
  awatch/pitomation:1.0.9 python \
  /app/__main__.py /config.yaml
