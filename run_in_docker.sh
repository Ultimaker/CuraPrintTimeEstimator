#!/usr/bin/env bash
# Copyright (c) 2018 Ultimaker B.V.

# build our tensorflow image
docker build --tag cura-print-time-estimator:local --file Dockerfile .

# download some models with our image first
docker run --rm -it \
    --volume $PWD:/srv/host \
    --entrypoint python3 \
    cura-print-time-estimator:local \
    main.py download

# then slice the models we downloaded using the Cura Docker image.
docker run --rm -it \
    --volume $PWD:/srv/host \
    --env CURA_ENGINE_SEARCH_PATH=/srv/cura/Cura/resources/extruders \
    --workdir /srv/host \
    --entrypoint python3 \
    ultimaker/cura:master-20180307 \
    main.py slice

# then analyze the models and their printing times
docker run --rm -it \
    --volume $PWD:/srv/host \
    --entrypoint python3 \
    cura-print-time-estimator:local \
    main.py analyze
