# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import trimesh


class GenerateCubes:
    """
    Generates scaled versions of a model
    """

    BASE_CUBE = "models/cube10.stl"
    SCALES = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    NAME_FORMAT = "models/cube{}0.stl"

    @staticmethod
    def run():
        GenerateCubes().generate()

    def generate(self) -> None:
        for scale in self.SCALES:
            mesh = trimesh.load(self.BASE_CUBE)  # type: trimesh.Trimesh
            mesh.apply_scale(scale)
            mesh.vertices -= mesh.center_mass
            file_name = self.NAME_FORMAT.format(scale)
            mesh.export(file_name)
            logging.info("Generated %s", file_name)
