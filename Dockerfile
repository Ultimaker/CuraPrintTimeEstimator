# Copyright (c) 2018 Ultimaker B.V.
FROM ultimaker/cura:master-20180307 AS base

# install requirements
RUN pip3 install --upgrade pip==9.0.*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy files
WORKDIR /srv/host/
CMD ["python3", "main.py"]
ADD . .
