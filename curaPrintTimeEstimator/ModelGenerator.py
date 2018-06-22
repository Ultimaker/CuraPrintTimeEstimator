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
    SCALES = [1 + i / 10.0 for i in range(1, 91)]   # increases by 10% every time

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

            name, _, ext = file_name.rpartition(".")
            new_file_name = "{0}{1:04.1f}.{2}".format(name, scale, ext)
            mesh.export(new_file_name)
            logging.info("Generated %s", new_file_name)
