#!/usr/bin/env python3
from collections import deque
import os
import subprocess
import tempfile
import time

import jinja2


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class MachineTemplateGenerator:

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self._template = None

    def load(self) -> None:
        with open(self.file_name, "r", encoding = "utf-8") as f:
            data = f.read()
        self._template = jinja2.Template(data)

    def generate(self, **kwargs) -> str:
        return self._template.render(**kwargs)


class Runner:

    def __init__(self, templates_dir: str, models_dir: str, results_dir: str) -> None:
        self.templates_dir = templates_dir
        self.models_dir = models_dir
        self.results_dir = results_dir

        self._temp_dir = ""

        self.model_file_list = []

    def start(self) -> None:
        # Create a temp dir to generate machine config files
        self._temp_dir = tempfile.mkdtemp(prefix = "cura-print-time-estimator-%s-" % time.time())

        os.makedirs(self.results_dir, exist_ok = True)

        self._get_all_model_files()

        self._get_next_template(self.templates_dir)

    def _get_all_model_files(self) -> None:
        for _, __, file_names in os.walk(self.models_dir):
            for file_name in file_names:
                if "sphere" in file_name.lower():
                    continue

                file_path = os.path.join(self.models_dir, file_name)
                self.model_file_list.append(file_path)
            break

    def _get_next_template(self, current_dir: str, prefixes = None) -> None:
        if prefixes is None:
            prefixes = deque()
        prefixes.append(os.path.basename(current_dir))

        for _, dir_names, file_names in os.walk(current_dir):
            template_file_names = [fn for fn in file_names if fn.endswith(".j2")]
            for template_file_name in template_file_names:
                template_file_path = os.path.join(current_dir, template_file_name)
                template_generator = MachineTemplateGenerator(template_file_path)
                template_generator.load()

                for infill_density in range(0, 105, 10):
                    template_content = template_generator.generate(infill_sparse_density = infill_density)
                    machine_file_path = os.path.join(self._temp_dir, "machine.yaml")
                    with open(machine_file_path, "w", encoding = "utf-8") as f:
                        f.write(template_content)

                    for model_file_path in self.model_file_list:
                        model_file_name = os.path.basename(model_file_path)
                        gcode_file_name = model_file_name.rsplit(".", 1)[0] + ("_infill_%s_" % infill_density) + ".gcode"
                        gcode_file_name = "_".join(prefixes) + "_" + gcode_file_name

                        self.run_cli(machine_file_path, model_file_path, gcode_file_name)

            for dir_name in dir_names:
                next_dir = os.path.join(current_dir, dir_name)
                self._get_next_template(next_dir, prefixes = [])

            break

        prefixes.pop()

    def run_cli(self, machine_file_path: str, model_file_path: str, result_file_name: str) -> None:
        cmd = ["docker", "run", "-t", "--rm"]
        cmd += ["--user", "1000:1000"]
        cmd += ["-v", "%s:/srv/machine.yaml" % os.path.abspath(machine_file_path)]
        cmd += ["-v", "%s:/srv/model.stl" % os.path.abspath(model_file_path)]
        cmd += ["-v", "%s:/srv/results:rw" % os.path.abspath(self.results_dir)]
        cmd += ["cura-cli"]
        cmd += ["--machine-yaml", "/srv/machine.yaml"]
        cmd += ["--model-file", "/srv/model.stl"]
        cmd += ["--output-file", "/srv/results/%s" % result_file_name]

        a = subprocess.Popen(cmd)
        a.communicate()


if __name__ == "__main__":
    result_dir = "results"

    runner = Runner(
        os.path.join(SCRIPT_DIR, "settings"),
        os.path.join(SCRIPT_DIR, "models"),
        os.path.join(result_dir)
    )

    runner.start()
