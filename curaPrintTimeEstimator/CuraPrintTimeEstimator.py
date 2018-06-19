# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from typing import Dict, Optional

from Settings import Settings

from curaPrintTimeEstimator.helpers.ModelStatisticsCalculator import ModelStatisticsCalculator
from curaPrintTimeEstimator.helpers.NeuralNetwork import NeuralNetwork


class CuraPrintTimeEstimator:
    """
    Main application file of the Cura Print time estimator.
    """

    # which files contain models
    FILENAME_FILTER = r".*\.(stl|obj)"

    # The file will contain the output of the time estimation (see self.gatherPrintTimeData)
    INPUT_FILE = "{}/print_times.json".format(Settings.PROJECT_DIR)

    # The class responsible for calculating statistics about the model.
    model_reader = ModelStatisticsCalculator()

    # Neural network
    neural_network = NeuralNetwork()

    @staticmethod
    def run() -> None:
        """
        Runs the application.
        """
        CuraPrintTimeEstimator().analyze()

    def analyze(self):
        with open(self.INPUT_FILE) as f:
            print_times = json.load(f)  # type: Dict[str, Dict[str, Dict[str, Optional[int]]]]

        statistics = {
            model_name: self.model_reader.read(model_name) for model_name in print_times
        }  # type: Dict[str, Dict[str, any]]

        self.neural_network.train(print_times, statistics)
