# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re
import sys
from subprocess import check_output, STDOUT
from typing import List

from Settings import Settings


class ModelTimeTester:
    """
    Class responsible for running the cura engine and parsing the expected print time returned.
    """

    def slice(self, model_name: str, definition: str, settings: List[str]) -> int:
        """
        Runs the slicer, returning the estimated amount of seconds to print the model.
        :param model_name: The name of the model, without the .stl extension.
        :param definition: The definition file to be used, without the .json extension.
        :param settings: The extra settings to be passed to the engine.
        :return: The amount of seconds Cura expects the printing will take.
        """

        logging.info("Slicing %s with definition %s and settings %s", model_name, definition, settings)

        arguments = [
            Settings.CURA_ENGINE,
            "slice", "-v",
            "-o", "NUL" if sys.platform == "win32" else "/dev/null",
            "-j", "{}/resources/definitions/{}.json".format(Settings.CURA_DIR, definition),
            "-e0", "-l", "{}/models/{}.stl".format(Settings.PROJECT_DIR, model_name)
        ]

        for s in settings:
            arguments.extend(["-s", s])

        output = check_output(arguments, stderr=STDOUT).decode()
        return self._parsePrintTime(output)

    @staticmethod
    def _parsePrintTime(cura_output: str) -> int:
        """
        Finds the expected print time in the output from the Cura engine.
        See tests/fixtures for examples of the output.
        :param cura_output: The output from the Cura Engine CLI.
        :return: The amount of seconds found in the output."""
        search = re.search(r"Print time: (\d+)\n", cura_output)
        if not search:
            raise ValueError("Cannot parse the cura output {}".format(cura_output))
        return int(search.group(1))
