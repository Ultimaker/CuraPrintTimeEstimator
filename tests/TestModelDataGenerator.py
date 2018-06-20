# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from unittest.mock import patch

from curaPrintTimeEstimator.ModelDataGenerator import ModelDataGenerator
from curaPrintTimeEstimator.helpers import findModels


class TestModelDataGenerator(TestCase):
    maxDiff = None

    @patch("curaPrintTimeEstimator.ModelDataGenerator.findModels")
    def test_run(self, find_models_mock):
        find_models_mock.return_value = ["cube10.stl", "cube20.stl"]
        ModelDataGenerator().run()

        with open(ModelDataGenerator.OUTPUT_FILE) as f:
            result = json.load(f)

        with open("tests/fixtures/expected_output.json") as f:
            expected = json.load(f)

        print(result)
        self.assertEqual(expected, result)

    def test_findModels(self):
        result = list(findModels())
        self.assertEqual(10, len(result))
