# Copyright (c) 2018 Ultimaker B.V.
FROM tensorflow/tensorflow:latest-py3 AS base

# install requirements
RUN pip3 install --upgrade pip==9.0.*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy files
WORKDIR /srv/host/
CMD ["python3", "main.py", "analyze"]
ADD . .
