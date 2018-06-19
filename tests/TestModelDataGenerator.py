# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from unittest.mock import patch

from Settings import Settings
from curaPrintTimeEstimator.ModelDataGenerator import ModelDataGenerator
from curaPrintTimeEstimator.helpers.ModelTimeCalculator import ModelTimeCalculator


class TestModelDataGenerator(TestCase):
    maxDiff = None

    @patch("curaPrintTimeEstimator.ModelTimeCalculator.ModelTimeCalculator._findModels")
    @patch("curaPrintTimeEstimator.helpers.ModelTimeTester.ModelTimeTester.slice")
    def test_run(self, slice_mock, find_models_mock):
        find_models_mock.return_value = ["3D_Printer_test", "jet_fighter", "cube10"]
        slice_mock.side_effect = range(100)
        ModelDataGenerator().run()

        with open(ModelDataGenerator.OUTPUT_FILE) as f:
            result = json.load(f)

        with open("tests/fixtures/expected_output.json") as f:
            expected = json.load(f)

        self.assertEqual(expected, result)

    def test__findModels(self):
        result = list(CuraPrintTimeEstimator._findModels())
        self.assertEqual(7, len(result))
