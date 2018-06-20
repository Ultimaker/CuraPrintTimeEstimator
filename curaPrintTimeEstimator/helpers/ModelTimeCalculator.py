# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os

from datetime import timedelta

import re
import sys
from subprocess import check_output, STDOUT, CalledProcessError
from typing import List, Dict, Optional, Iterable, Tuple

from Settings import Settings
from curaPrintTimeEstimator.helpers import findModels


class ModelTimeCalculator:
    """
    Class responsible for running the cura engine for all models found in the 'models' directory.
    The results are parsed and the expected print time is written to an output file.
    """

    # which definition files should be used, excluding the .def.json extension.
    DEFINITIONS = ("fdmprinter", )

    # The file will contain the output of the time estimation (see self.gatherPrintTimeData)
    OUTPUT_FILE = "{}/print_times.json".format(Settings.PROJECT_DIR)

    def __init__(self):
        self.settings = dict(self._findSettings())

    @staticmethod
    def run() -> None:
        """
        Runs the application.
        """
        ModelTimeCalculator().gatherData()

    def gatherData(self) -> Dict[str, Dict[str, Dict[str, Optional[int]]]]:
        """
        Gathers data about the estimated print time for one model, all settings and all definitions.
        :return: A dict with the format {
            model_name: {
                definition: {settings_name: print_time},
            }
        }.
        """
        settings = dict(self._findSettings())

        if os.path.exists(self.OUTPUT_FILE):
            with open(self.OUTPUT_FILE) as f:
                result = json.load(f)
        else:
            result = {}

        try:
            for model in findModels():
                result[model] = self.gatherPrintTimeData(model, settings, prev_results=result.get(model))
        finally:
            with open(self.OUTPUT_FILE, "w") as f:
                json.dump(result, f, indent=2)
            logging.info("Results written to %s", self.OUTPUT_FILE)

        return result

    @staticmethod
    def _findSettings() -> Iterable[Tuple[str, List[str]]]:
        """
        Finds the TXT files available in the 'settings' sub folder.
        :return: An iterable of lists of settings each format: (settings_name, settings_parameters).
        """
        directory = "{}/settings".format(Settings.PROJECT_DIR)
        files = os.listdir(directory)
        for name in sorted(files):
            if name.endswith(".txt"):
                with open("{}/{}".format(directory, name)) as f:
                    yield name[:-4], f.readlines()

    def gatherPrintTimeData(self, model: str, settings: Dict[str, List[str]],
                            prev_results: Optional[Dict[str, Dict[str, Optional[int]]]]
                            ) -> Dict[str, Dict[str, Optional[int]]]:
        """
        Gathers data about the estimated print time for one model, all settings and all definitions.
        :param model: The name of the model file, including the extension.
        :param settings: A dict with the settings file name and a list of settings for each of the files.
        :return: A dict with the format {definition: {settings_name: print_time}}.
        """
        result = prev_results or {}
        for definition in self.DEFINITIONS:
            result.setdefault(definition, {})
            for setting_name, settings_parameters in settings.items():
                if result[definition].get(setting_name):
                    logging.info("Model %s, definition %s and settings %s was already sliced, %s seconds to print.",
                                 model, definition, settings, result[definition][setting_name])
                else:
                    result[definition][setting_name] = self.slice(model, definition, settings_parameters)
        return result

    def slice(self, model_name: str, definition: str, settings: List[str]) -> Optional[int]:
        """
        Runs the slicer, returning the estimated amount of seconds to print the model.
        :param model_name: The name of the model including the extension.
        :param definition: The definition file to be used, without the .def.json extension.
        :param settings: The extra settings to be passed to the engine.
        :return: The amount of seconds Cura expects the printing will take.
        """
        logging.info("Slicing %s with definition %s and settings %s", model_name, definition, settings)

        arguments = [
            Settings.CURA_ENGINE,
            "slice", "-v",
            "-o", "NUL" if sys.platform == "win32" else "/dev/null",
            "-j", os.path.join(Settings.CURA_DIR, "resources", "definitions", "{}.def.json".format(definition)),
        ]

        # Add the global settings
        for s in settings:
            arguments.extend(["-s", s])

        # Add the extruder0 settings
        for s in settings:
            arguments.extend(["-e0", "-s", s])

        arguments.extend(["-e0", "-l", os.path.join(Settings.PROJECT_DIR, "models", model_name)])

        try:
            output = check_output(arguments, stderr=STDOUT).decode()
        except CalledProcessError as err:
            if b"Failed to load model:" in err.output:
                logging.warning("Cannot load model %s: %s", model_name, err.output)
                return None
            else:
                logging.error(err.output)
                raise
        return self._parsePrintTime(output)

    @staticmethod
    def _parsePrintTime(cura_output: str) -> int:
        """
        Finds the expected print time in the output from the Cura engine.
        See tests/fixtures for examples of the output.
        :param cura_output: The output from the Cura Engine CLI.
        :return: The amount of seconds found in the output."""
        search = re.search(r"Print time: (\d+)\r?\n", cura_output)
        if not search:
            raise ValueError("Cannot parse the cura output {}".format(cura_output))
        result = int(search.group(1))
        logging.info("Model will be printed in %s", timedelta(seconds=result))
        return result
