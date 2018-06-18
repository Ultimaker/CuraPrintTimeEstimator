#!/usr/bin/env bash
# Copyright (c) 2018 Ultimaker B.V.

docker build --tag cura-print-time-estimator:local .

docker run -it \
    --volume $PWD:/srv/host \
    --env CURA_ENGINE_SEARCH_PATH=/srv/cura/Cura/resources/extruders \
    --workdir /srv/host \
    --entrypoint python3 \
    cura-print-time-estimator:local scripts/download_models.py
