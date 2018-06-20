# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import copy
from typing import List, Dict, Tuple, Optional
from sklearn.model_selection import train_test_split

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

    SETTINGS_DIR = "{}/settings".format(Settings.PROJECT_DIR)

    def run(self) -> None:
        inputs, targets = self._flattenData(self._getMask())
        x_train, x_test, y_train, y_test = train_test_split(inputs, targets, test_size = 0.25)
        logging.info("These are the inputs and target for the NN:\nINPUTS: {inputs}\nTARGETS: {targets}"
                     .format(inputs=inputs, targets=targets))

        neural_network = CuraNeuralNetworkModel(len(inputs[0]), 1)
        neural_network.train(x_train, y_train)
        neural_network.validate(x_test, y_test)

    def _getMask(self) -> Dict[str, List[str]]:
        """
        Loads the settings we are using for train the the regression algorithm.
        :return: The parsed contents of the mask file.
        """
        with open(CuraPrintTimeEstimator.MASK_FILE) as f:
            return json.load(f)

    def _flattenData(self, mask_data: Dict[str, List[str]]) -> Tuple[List[List[Optional[float]]], List[List[float]]]:
        """
        Organizes the data collected in previous steps in inputs and target values.
        :return: A list of values used as the input for the NN and the printing times as the target values
        """
        inputs = []
        targets = []

        with open(CuraPrintTimeEstimator.INPUT_FILE) as f:
            data = json.load(f)

        for model_name, model_data in data.items():
            # Use the statistics that are the same for the same model
            model_stats = list(model_data["model_statistics"][key] for key in mask_data["model_statistics"])

            for definition, settings_profiles in model_data["print_times"].items():
                for settings_profile, print_time in settings_profiles.items():
                    if not print_time:
                        continue
                    targets.append(print_time)   # We store the target times

                    # Take the values from the setting profiles that are in the mask
                    settings = self._readSettings(settings_profile)

                    settings_data = [settings.get(mask_setting) for mask_setting in mask_data["settings"]]
                    inputs.append(list(model_stats) + settings_data)

        return inputs, targets

    def _readSettings(self, settings_profile: str) -> Dict[str, float]:
        with open("{}/{}.txt".format(self.SETTINGS_DIR, settings_profile)) as s:
            contents = [l.split("=", 2) for l in s.readlines()]  # type: List[Tuple[str, str]]

        return {key.rstrip(): float(value.lstrip()) for key, value in contents}
