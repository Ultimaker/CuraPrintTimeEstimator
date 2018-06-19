# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

if __name__ == "__main__":
    app = sys.argv[1]
    if app == "download":
        from curaPrintTimeEstimator.helpers.ThingiverseModelDownloader import ThingiverseModelDownloader
        ThingiverseModelDownloader.run()
    elif app == "slice":
        from curaPrintTimeEstimator.helpers.ModelTimeTester import ModelTimeTester
        ModelTimeTester.run()
    elif app == "analyze":
        from curaPrintTimeEstimator.CuraPrintTimeEstimator import CuraPrintTimeEstimator
        CuraPrintTimeEstimator.run()
    else:
        raise ValueError("Please pass either 'download', 'slice' or 'analyze' as parameter.")
