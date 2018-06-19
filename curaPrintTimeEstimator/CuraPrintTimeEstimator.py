# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import copy
from typing import List, Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf

from Settings import Settings
from curaPrintTimeEstimator.ModelDataGenerator import ModelDataGenerator
from curaPrintTimeEstimator.neuralnetwork.CuraNeuralNetworkModel import CuraNeuralNetworkModel


class CuraPrintTimeEstimator:
    """
    Main application file to run the estimator. It includes read the data that was generated in previous steps, train
    the NN and make a test/validation process.
    """

    # The file that contains the input settings for the training data
    MASK_FILE = "{}/mask.json".format(Settings.PROJECT_DIR)

    # The file that contains information we gather in a previous step
    INPUT_FILE = ModelDataGenerator.OUTPUT_FILE

    def __init__(self):
        self.inputs, self.targets = self._parseData(self._mask())
        logging.info("These are the inputs and target for the NN:\nINPUTS: {inputs}\n\nTARGETS: {targets}".format(inputs=self.inputs, targets=self.targets))
        self.neural_network = CuraNeuralNetworkModel(len(self.inputs[0]), 1, 10)

    def run(self) -> None:
        self.neural_network.train()

    def train(self) -> None:
        X_train, X_test, y_train, y_test = train_test_split(self.inputs, self.targets, test_size = 0.25)

    def _mask(self) -> Dict[str, List[str]]:
        """
        Loads the settings we are using for train the the regression algorithm.
        :return: An iterable of lists of settings each format: (settings_name, settings_parameters).
        """
        with open(CuraPrintTimeEstimator.MASK_FILE) as f:
            return json.load(f)

    def _parseData(self, mask_data: Dict[str, List[str]]) -> Tuple[List[List[float]], List[float]]:
        """
        Organizes the data collected in previous steps in inputs and target values.
        :return: A list of values used as the input for the NN and the printing times as the target values
        """
        inputs = []
        targets = []

        with open(CuraPrintTimeEstimator.INPUT_FILE) as f:
            data = json.load(f)
            for model_name in data:
                model_data = data[model_name]
                statistics = []
                # Take some model statistics as inputs as indicated in the mask
                for mask_model_stat in mask_data["model_statistics"]:
                    statistics.append(model_data["model_statistics"][mask_model_stat])

                for definition in model_data["print_times"]:
                    for settings_profile in model_data["print_times"][definition]:
                        targets.append(model_data["print_times"][definition][settings_profile])   # We store the target times
                        # Use the statistics that are the same for the same model
                        input = copy.copy(statistics)

                        # Take the values from the setting profiles that are in the mask
                        settings_directory = "{}/settings".format(Settings.PROJECT_DIR)
                        with open("{}/{}.txt".format(settings_directory, settings_profile)) as s:
                            contents = s.readlines()
                            for mask_setting in mask_data["settings"]:
                                value = self._findSettingValue(contents, mask_setting)
                                if value:
                                    input.append(value)

                        inputs.append(input)
        return inputs, targets


    def _findSettingValue(self, contents: List[str], setting: str) -> Optional[float]:
        for line in contents:
            name, value = line[:line.find("=")].rstrip(), line[line.find("=")+1:].lstrip()
            if name == setting:
                return float(value)
        return None

