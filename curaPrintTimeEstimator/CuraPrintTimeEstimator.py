# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
from typing import Iterable, List, Dict

from Settings import Settings
from curaPrintTimeEstimator.helpers.ModelTimeTester import ModelTimeTester


class CuraPrintTimeEstimator:
    """
    Main application file of the Cura Print time estimator.
    """


    # which definition files should be used, excluding the .json extension.
    DEFINITIONS = (
        "ultimaker3.def",
    )

    # the different settings that we want to test.
    SETTINGS = {
        "basic": ["infill_line_distance=0"]
    }  # type: Dict[str, List[str]]

    # The file will contain the output of the time estimation (see self.gatherPrintTimeData)
    TIMINGS_FILE = "{}/output.json".format(Settings.PROJECT_DIR)

    # The class responsible for actually slicing.
    slicer = ModelTimeTester()

    def run(self) -> None:
        """
        Runs the application.
        """
        self.gatherPrintTimeData()

    @staticmethod
    def _findModels() -> Iterable[str]:
        """
        Finds the STL files available in the 'models' sub folder.
        :return: An iterable of model strings.
        """
        files = os.listdir("{}/models".format(Settings.PROJECT_DIR))
        for model in sorted(files):
            if model.endswith(".stl"):
                yield model[:-4]

    def gatherPrintTimeData(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """
        Gathers data about the estimated print time for all models.
        :return: A dict with the format {settings_name: {definition: {model_name: print_time}}}.
        """
        result = {}
        for model in self._findModels():
            for setting_name, settings_parameters in self.SETTINGS.items():
                for definition in self.DEFINITIONS:
                    print_time = self.slicer.slice(model, definition, settings_parameters)
                    result.setdefault(setting_name, {}).setdefault(definition, {})[model] = print_time

        with open(self.TIMINGS_FILE, "w") as f:
            json.dump(result, f, indent=2)
        logging.info("Results written to %s", self.TIMINGS_FILE)
        return result
