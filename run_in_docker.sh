#!/usr/bin/env bash
# Copyright (c) 2018 Ultimaker B.V.

echo " ****** Running tests ****** "
docker build \
    --tag cura-print-time-estimator:tests \
    --file Dockerfile.tests . \
    || exit $?  # TODO: use main image.

echo " ****** Building our tensorflow image ****** "
docker build \
    --tag cura-print-time-estimator:local \
    --file Dockerfile . \
    || exit $?

echo " ****** Generating test models ****** "
docker run --rm -it \
    --volume $PWD:/srv/host \
    --entrypoint python3 \
    cura-print-time-estimator:local \
    main.py cubes \
    || exit $?

echo " ****** Slicing all models ****** "
docker run --rm -it \
    --volume $PWD:/srv/host \
    --env CURA_ENGINE_SEARCH_PATH=/srv/cura/Cura/resources/extruders \
    --workdir /srv/host \
    --entrypoint python3 \
    ultimaker/cura:master-20180307 \
    main.py slice \
    || exit $?

echo " ****** Generating test data ****** "
docker run --rm -it \
    --volume $PWD:/srv/host \
    --entrypoint python3 \
    cura-print-time-estimator:local \
    main.py generate \
    || exit $?

echo " ****** Running neural network to estimate print times ****** "
docker run --rm -it \
    --volume $PWD:/srv/host \
    --entrypoint python3 \
    cura-print-time-estimator:local \
    main.py estimate \
    || exit $?
