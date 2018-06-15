# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import patch

from curaPrintTimeEstimator.helpers.ModelTimeTester import ModelTimeTester


class TestModelTimeTester(TestCase):

    @patch("curaPrintTimeEstimator.helpers.ModelTimeTester.check_output")
    def test_slice(self, cura_mock):
        with open("tests/fixtures/3D_Printer_test.out", "rb") as f:
            cura_mock.return_value = f.read()

        tester = ModelTimeTester()
        result = tester.slice("3D_Printer_test", "definition", ["settings1", "settings2"])
        self.assertEqual(33111, result)

        expected_params = [
            '/srv/cura/CuraEngine/build/CuraEngine', 'slice', '-v', '-o', '/dev/null',
            '-j', '/srv/cura/Cura/resources/definitions/definition.json',
            '-e1', '-e0', '-l', '/usr/src/app/models/3D_Printer_test.stl',
            '-s', 'settings1', '-s', 'settings2'
        ]

        cura_mock.assert_called_once_with(expected_params, stderr=-2)

    @patch("curaPrintTimeEstimator.helpers.ModelTimeTester.check_output")
    def test_slice_error(self, cura_mock):
        with open("tests/fixtures/jet_fighter-error.out", "rb") as f:
            cura_mock.return_value = f.read()

        tester = ModelTimeTester()
        with self.assertRaises(ValueError):
            tester.slice("3D_Printer_test", "definition", ["settings1", "settings2"])