#!/usr/bin/env bash
# Copyright (c) 2018 Ultimaker B.V.

docker run -it --entrypoint python3 \
    --volume $PWD/cura-files:/srv/cura/host \
    --env CURA_ENGINE_SEARCH_PATH=/srv/cura/Cura/resources/extruders \
    --workdir /srv/cura/CuraEngine \
    ultimaker/cura:master-20180307 \
    /srv/cura/host/run_in_docker.py
