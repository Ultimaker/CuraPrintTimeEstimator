# Copyright (c) 2018 Ultimaker B.V.
FROM ultimaker/cura:master-20180307 AS base

# install requirements
RUN pip3 install --upgrade pip==9.0.*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
#RUN python3 --version
#RUN python3 -c "from pip import pep425tags;print(pep425tags.supported_tags) "
##RUN pip3 install --upgrade tensorflow
#RUN pip3 install --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.8.0-cp35-cp35m-linux_x86_64.whl

# copy files
WORKDIR /srv/host/
CMD ["python3", "main.py"]
ADD . .
