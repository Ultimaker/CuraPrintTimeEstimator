# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from typing import List, Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import numpy as np

from Settings import Settings
from curaPrintTimeEstimator.ModelDataGenerator import ModelDataGenerator
from curaPrintTimeEstimator.helpers import findModels
from curaPrintTimeEstimator.helpers.ModelTimeCalculator import ModelTimeCalculator
from curaPrintTimeEstimator.neuralnetwork.CuraNeuralNetworkModel import CuraNeuralNetworkModel


class CuraPrintTimeEstimator:
    """
    Main application file to run the estimator. It includes read the data that was generated in previous steps, train
    the NN and make a test/validation process.
    """

    # The file that contains the input settings for the training data
    MASK_FILE = "{}/mask.json".format(Settings.PROJECT_DIR)

    # The file that contains information we gather in a previous step
    STATS_FILE = ModelDataGenerator.OUTPUT_FILE
    SLICE_FILE = ModelTimeCalculator.OUTPUT_FILE

    SETTINGS_DIR = "{}/settings".format(Settings.PROJECT_DIR)

    def run(self) -> None:
        inputs, targets = self._flattenData(self._getMask())
        X_train, X_test, y_train, y_test = train_test_split(inputs, targets, test_size = 0.25)
        logging.info("These are the inputs and target for the NN:\nINPUTS: {inputs}\nTARGETS: {targets}"
                     .format(inputs=inputs, targets=targets))

        # Normalize training data
        scaler = MinMaxScaler()
        X_train_minmax = scaler.fit_transform(X_train)
        X_test_minmax = scaler.fit_transform(X_test)
        neural_network = CuraNeuralNetworkModel(len(inputs[0]), len(targets[0]), [10, 5])
        logging.debug("Minimum {min}:".format(min = np.min(inputs, axis = 0)))
        logging.debug("Maximum {max}:".format(max = np.max(inputs, axis = 0)))
        neural_network.train(X_train_minmax, y_train)
        neural_network.validate(X_test_minmax, y_test)
        # print("This is the predicted value:", neural_network.predict([[0.49253, 0.6203, 0.0, 0.01316]]))

    def _getMask(self) -> Dict[str, Dict[str, bool]]:
        """
        Loads the settings we are using for train the the regression algorithm.
        :return: The parsed contents of the mask file.
        """
        with open(CuraPrintTimeEstimator.MASK_FILE) as f:
            return json.load(f)

    def _flattenData(self, mask_data: Dict[str, Dict[str, bool]]) -> Tuple[List[List[Optional[float]]], List[List[float]]]:
        """
        Organizes the data collected in previous steps in inputs and target values.
        :return: A list of values used as the input for the NN and the printing times as the target values
        """
        inputs = []
        targets = []

        with open(CuraPrintTimeEstimator.STATS_FILE) as f:
            stats_data = json.load(f)

        with open(CuraPrintTimeEstimator.SLICE_FILE) as f:
            slice_data = json.load(f)

        for model_name in findModels():
            if model_name not in stats_data:
                logging.warning("Cannot find stats for %s", model_name)
                continue
            if model_name not in slice_data:
                logging.warning("Cannot find print times for %s", model_name)
                continue

            # Use the statistics that are the same for the same model
            model_stats = list(stats_data[model_name][key] for key in mask_data["model_statistics"])

            for definition, settings_profiles in slice_data[model_name].items():
                for settings_profile, print_time in settings_profiles.items():
                    if not print_time:
                        continue
                    targets.append([print_time / 3600])   # We store print time as a list, in hours

                    # Take the values from the setting profiles that are in the mask
                    settings = self._readSettings(settings_profile)

                    # settings_data = [1 / settings.get(mask_setting) if is_inverse else settings.get(mask_setting) for mask_setting, is_inverse in mask_data["settings"].items()]
                    settings_data = [settings.get(mask_setting) for mask_setting, is_inverse in mask_data["settings"].items()]
                    inputs.append(list(model_stats) + settings_data)

        return inputs, targets

    def _readSettings(self, settings_profile: str) -> Dict[str, float]:
        with open("{}/{}.txt".format(self.SETTINGS_DIR, settings_profile)) as s:
            contents = [line.split("=", 2) for line in s.readlines()]  # type: List[Tuple[str, str]]

        return {key.rstrip(): float(value.lstrip()) for key, value in contents}

