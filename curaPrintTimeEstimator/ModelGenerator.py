# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

import trimesh


class ModelGenerator:
    """
    Generates scaled versions of a model
    """
    SCALES = [i / 10.0 for i in range(1, 101) if i != 10.0]

    @staticmethod
    def run():
        generator = ModelGenerator()
        generator.generate("cube.stl")
        generator.generate("sphere.stl")

    def generate(self, model_name) -> None:
        for scale in self.SCALES:
            file_name = os.path.join("models", model_name)
            mesh = trimesh.load(file_name)  # type: trimesh.Trimesh
            mesh.apply_scale(scale)
            mesh.vertices -= mesh.center_mass
            new_file_name = file_name.replace(".stl", "{0:04.1f}.stl".format(scale))
            mesh.export(new_file_name)
            logging.info("Generated %s", new_file_name)
