#!/usr/bin/env bash
import json
import logging
import os
import re
from subprocess import check_output, STDOUT
from typing import Dict, Iterable


class ModelTimeTester:

    def printTimeAllModels(self) -> Dict[str, int]:
        result = {}
        for model in self._findModels():
            output = self.slice(model)
            print_time = self._parsePrintTime(output)
            result[model] = print_time
        return result

    def _findModels(self) -> Iterable[str]:
        for model in os.listdir("../host/models"):
            if model.endswith(".stl"):
                yield model[:-4]

    def slice(self, model_name: str):
        logging.info("Parsing")
        return check_output([
            "./build/CuraEngine", "slice", "-v", "-j", "../Cura/resources/definitions/ultimaker3.def.json", "-e1", "-s",
            "infill_line_distance=0", "-e0", "-l", "../host/models/{}.stl".format(model_name)
        ], stderr=STDOUT).decode()

    def _parsePrintTime(self, cura_output):
        return int(re.search(r"Print time: (\d+)", cura_output).group(1))


if __name__ == "__main__":
    result = ModelTimeTester().printTimeAllModels()
    print(json.dumps(result, indent=2))
