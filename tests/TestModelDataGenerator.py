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

    @patch("curaPrintTimeEstimator.helpers.ModelTimeCalculator.ModelTimeCalculator.slice")
    def test_run(self, slice_mock):
        slice_mock.side_effect = range(100)
        ModelDataGenerator().run()

        with open(ModelDataGenerator.OUTPUT_FILE) as f:
            result = json.load(f)

        with open("tests/fixtures/expected_output.json") as f:
            expected = json.load(f)

        self.assertEqual(expected, result)
