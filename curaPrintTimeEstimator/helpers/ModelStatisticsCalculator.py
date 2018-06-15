# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Union

import trimesh


class ModelStatisticsCalculator:
    """
    Class responsible for calculating statistics about models.
    """

    def __init__(self):
        trimesh.util.attach_to_log()

    def read(self, model: str) -> Dict[str, Union[int, float]]:
        """
        Gathers statistics about the model.
        :param model: The name of the model file, without the .stl extension.
        :return: The statistics about the model with format: {name: value}.
        """
        mesh = trimesh.load('models/{}.stl'.format(model))  # type: trimesh.Trimesh
        return {
            "volume": mesh.volume,
            "surface_area": mesh.area,
            "area_faces": mesh.area_faces.size,
            "box_volume": mesh.bounding_box.volume,
            "edges": mesh.edges.size,
            "mass": mesh.mass,
            "vertices": mesh.vertices.size,
        }
