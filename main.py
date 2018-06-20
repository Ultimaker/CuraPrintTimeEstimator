# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

if __name__ == "__main__":
    app = sys.argv[1]
    if app == "models":
        from curaPrintTimeEstimator.ModelGenerator import ModelGenerator
        ModelGenerator.run()
    elif app == "slice":
        from curaPrintTimeEstimator.helpers.ModelTimeCalculator import ModelTimeCalculator
        ModelTimeCalculator.run()
    elif app == "generate":
        from curaPrintTimeEstimator.ModelDataGenerator import ModelDataGenerator
        ModelDataGenerator.run()
    elif app == "estimate":
        from curaPrintTimeEstimator.CuraPrintTimeEstimator import CuraPrintTimeEstimator
        CuraPrintTimeEstimator().run()
    else:
        raise ValueError("Please pass either 'download', 'slice' or 'analyze' as parameter.")
