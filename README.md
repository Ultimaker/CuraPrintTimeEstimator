# Cura Print Time Estimator
This repository is part of a research to try to better estimate the printing time of complex models.

The repository will contain code to gather and process data to create models that predict how long a model will take to be 3D-printed given some specific Cura settings.

## Running it locally
You may run the application with docker:
```
./run_in_docker.sh
```

If you have Cura environment in your local machine you may also run the application outside docker, by setting the Cura directory in the environment variable `CURA_DIR`:
```
CURA_DIR="/cura/" python3 main.py
```
