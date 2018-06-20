# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
from typing import Iterable, List, Dict, Tuple

from Settings import Settings
from curaPrintTimeEstimator.helpers.ModelTimeCalculator import ModelTimeCalculator
from curaPrintTimeEstimator.helpers.ModelStatisticsCalculator import ModelStatisticsCalculator


class ModelDataGenerator:
    """
    Main application file to generate data for the Cura Print time estimator.
    """

    # which definition files should be used, excluding the .def.json extension.
    DEFINITIONS = ("fdmprinter", )

    # The file will contain the output of the time estimation (see self.gatherPrintTimeData)
    OUTPUT_FILE = "{}/output.json".format(Settings.PROJECT_DIR)

    # The class responsible for actually slicing.
    slicer = ModelTimeCalculator()

    # The class responsible for calculating statistics about the model.
    stats_calc = ModelStatisticsCalculator()

    @staticmethod
    def run() -> None:
        """
        Runs the application.
        """
        ModelDataGenerator().gatherData()

    def gatherData(self) -> Dict[str, Dict[str, Dict[str, any]]]:
        """
        Gathers data about the estimated print time for one model, all settings and all definitions.
        :return: A dict with the format {
            model_name: {
                "print_times": {
                    definition: {settings_name: print_time},
                },
                "model_statistics": See `ModelStatisticsCalculator`.
            }
        }.
        """
        result = {}
        for model_name, print_times in ModelTimeCalculator().gatherData().items():
            if not os.path.exists(os.path.join("models", model_name)):
                logging.warning("Cannot find model %s", model_name)
                continue
            result[model_name] = {
                "print_times": print_times,
                "model_statistics": self.stats_calc.read(model_name),
            }

        with open(self.OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=2)
        logging.info("Results written to %s", self.OUTPUT_FILE)
        return result
