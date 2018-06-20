# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(module)s:%(lineno)s: %(message)s",
                    level=os.getenv("LOGGING_LEVEL", "DEBUG"))

class Settings:
    """
    Keeps the application settings.
    """

    PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
    CURA_DIR = os.getenv("CURA_DIR", "/srv/cura/Cura")
    CURA_ENGINE = os.getenv("CURA_ENGINE", "/srv/cura/CuraEngine/build/CuraEngine")
