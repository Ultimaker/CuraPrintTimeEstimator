# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
from typing import Iterable, List, Dict

from Settings import Settings
from curaPrintTimeEstimator.helpers.ModelTimeTester import ModelTimeTester
from curaPrintTimeEstimator.helpers.ModelStatisticsCalculator import ModelStatisticsCalculator

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
        "basic": ["infill_line_distance=0"],
        "default": [],
    }  # type: Dict[str, List[str]]

    # The file will contain the output of the time estimation (see self.gatherPrintTimeData)
    OUTPUT_FILE = "{}/output.json".format(Settings.PROJECT_DIR)

    # The class responsible for actually slicing.
    slicer = ModelTimeTester()

    # The class responsible for calculating statistics about the model.
    model_reader = ModelStatisticsCalculator()

    def run(self) -> None:
        """
        Runs the application.
        """
        self.gatherData()

    def gatherData(self) -> Dict[str, Dict[str, Dict[str, any]]]:
        """
        Gathers data about the estimated print time for one model, all settings and all definitions.
        :return: A dict with the format {
            model_name: {
                "print_times": {
                    definition: {settings_name: print_time},
                },
                "model_statistics": {""} TODO
            }
        }.
        """
        result = {}
        for model in self._findModels():
            result[model] = {
                "print_times": self.gatherPrintTimeData(model),
                "model_statistics": self.gatherModelStatistics(model),
            }

        with open(self.OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=2)
        logging.info("Results written to %s", self.OUTPUT_FILE)
        return result

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

    def gatherModelStatistics(self, model) -> Dict[str, any]:
        """
        Gathers data about the model.
        :param model: The name of the model file, without the .stl extension.
        :return: The statistics about the model.
        """
        return self.model_reader.read(model)

    def gatherPrintTimeData(self, model) -> Dict[str, Dict[str, int]]:
        """
        Gathers data about the estimated print time for one model, all settings and all definitions.
        :param model: The name of the model file, without the .stl extension.
        :return: A dict with the format {definition: {settings_name: print_time}}.
        """
        result = {}
        for definition in self.DEFINITIONS:
            result[definition] = {}
            for setting_name, settings_parameters in self.SETTINGS.items():
                result[definition][setting_name] = self.slicer.slice(model, definition, settings_parameters)
        return result