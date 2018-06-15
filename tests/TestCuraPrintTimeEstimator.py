# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
from typing import Iterable, List, Dict
from unittest import TestCase
from unittest.mock import patch

from Settings import Settings
from curaPrintTimeEstimator.CuraPrintTimeEstimator import CuraPrintTimeEstimator
from curaPrintTimeEstimator.helpers.ModelTimeTester import ModelTimeTester


class TestCuraPrintTimeEstimator(TestCase):
    maxDiff = None

    @patch("curaPrintTimeEstimator.helpers.ModelTimeTester.ModelTimeTester.slice")
    def test_run(self, slice_mock):
        slice_mock.side_effect = range(100)
        CuraPrintTimeEstimator().run()

        with open(CuraPrintTimeEstimator.OUTPUT_FILE) as f:
            result = json.load(f)
        print(result)

        with open("tests/fixtures/expected_output.json") as f:
            expected = json.load(f)

        self.assertEqual(expected, result)
