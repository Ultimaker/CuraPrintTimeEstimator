# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from typing import Dict

from Settings import Settings
from curaPrintTimeEstimator.helpers import findModels
from curaPrintTimeEstimator.helpers.ModelStatisticsCalculator import ModelStatisticsCalculator


class ModelDataGenerator:
    """
    Main application file to generate data for the Cura Print time estimator.
    """

    # The file will contain the output of the time estimation (see self.gatherPrintTimeData)
    OUTPUT_FILE = "{}/model_statistics.json".format(Settings.PROJECT_DIR)

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
            model_name: {See `ModelStatisticsCalculator`}
        }.
        """
        result = {model: self.stats_calc.read(model) for model in findModels()}

        with open(self.OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=2)
        logging.info("Results written to %s", self.OUTPUT_FILE)
        return result
