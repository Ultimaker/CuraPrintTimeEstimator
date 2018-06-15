# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os


class Settings:
    """
    Keeps the application settings.
    """

    PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
    CURA_DIR = os.getenv("CURA_DIR", "/srv/cura")
    CURA_ENGINE = os.getenv("CURA_ENGINE", "{}/CuraEngine/build/CuraEngine".format(CURA_DIR))
