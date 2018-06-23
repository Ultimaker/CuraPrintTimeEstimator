# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

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
        :param model: The name of the model file including the extension.
        :return: The statistics about the model with format: {name: value}.
        """
        file_name = 'models/{}'.format(model)
        file_size = os.path.getsize(file_name)
        mesh = trimesh.load(file_name)  # type: trimesh.Trimesh
        return {
            "volume": mesh.volume / 1000,
            "surface_area": mesh.area / 100,
            "area_faces": mesh.area_faces.size,
            "box_volume": mesh.bounding_box.volume / 1000,
            "edges": mesh.edges.size,
            "mass": mesh.mass,
            "vertices": mesh.vertices.size,
            "file_size": file_size,
            "volume_by_surface_area": mesh.volume / mesh.area,
        }
