# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from curaPrintTimeEstimator.ModelDataGenerator import ModelDataGenerator

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(module)s:%(lineno)s: %(message)s",
                        level=os.getenv("LOGGING_LEVEL", "DEBUG"))
    ModelDataGenerator().run()
