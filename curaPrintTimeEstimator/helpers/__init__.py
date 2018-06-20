# Copyright (c) 2018 Ultimaker B.V.
import os
import re
from typing import Iterable

from Settings import Settings


def findModels() -> Iterable[str]:
    """
    Finds the STL files available in the 'models' sub folder.
    :return: An iterable of model names.
    """
    files = os.listdir("{}/models".format(Settings.PROJECT_DIR))
    search = re.compile(r".*\.(stl|obj)", re.IGNORECASE)
    for model in sorted(files, key=str.casefold):
        if search.match(model):
            yield model
