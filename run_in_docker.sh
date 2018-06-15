#!/usr/bin/env bash
# Copyright (c) 2018 Ultimaker B.V.

docker run -it --entrypoint python3 \
    --volume $PWD:/srv/host \
    --env CURA_ENGINE_SEARCH_PATH=/srv/cura/Cura/resources/extruders \
    --workdir /srv/host \
    ultimaker/cura:master-20180307 \
    /srv/host/main.py
