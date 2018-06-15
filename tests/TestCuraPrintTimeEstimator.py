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
        slice_mock.side_effect = range(5)
        CuraPrintTimeEstimator().run()

        with open(CuraPrintTimeEstimator.TIMINGS_FILE) as f:
            result = f.read()

        expected = {
            'basic': {
                'ultimaker3.def': {
                    '3D_Printer_test': 0,
                    'Air_Spinner_2_-_Hollow': 1,
                    'BASKET-OPTO': 2,
                    'jet_fighter': 3,
                    'jet_fighter_egg': 4,
                }
            }
        }
        self.assertEqual(expected, json.loads(result))
