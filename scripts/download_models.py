# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from time import sleep
from urllib.parse import urlencode

import shutil

import requests
import sys

from argparse import ArgumentParser
from typing import Optional, Dict, Tuple

from Settings import Settings


class GooglePolyModelDownloader:
    FILENAME_ALLOWED_CHARS = (' ', '.', '_')  # letters and numbers are allowed besides these
    SLEEP_TIME = 0.1  # respect 10 requests per second limit.
    PAGE_SIZE = 100

    def __init__(self, api_key: str):
        self._api_key = api_key

    def downloadModels(self, count: int) -> None:
        downloaded_count = 0
        next_page_token = None
        while downloaded_count < count:
            models, resources, next_page_token = self._listModelUrls(next_page_token)
            for resource_name, resource_url in resources.items():
                self._download(resource_name, resource_url)
            for model_name, model_url in models.items():
                self._download(model_name, model_url)
                downloaded_count += 1
                if downloaded_count == count:
                    break

    def _download(self, name, url):
        safe_name = "".join(c for c in name if c.isalnum() or c in self.FILENAME_ALLOWED_CHARS).strip()
        file_name = "{}/models/{}".format(Settings.PROJECT_DIR, safe_name)
        if os.path.exists(file_name):
            return logging.info("The file %s already exists.", file_name)

        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise ValueError("Received unexpected HTTP {} from {}: {}"
                             .format(response.status_code, url, response.text))

        sleep(self.SLEEP_TIME)
        logging.info("Downloading %s from %s", name, url)
        with open(file_name, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

    def _listModelUrls(self, page_token: Optional[str] = None) -> Tuple[Dict[str, str], Dict[str, str], str]:
        params = {"key": self._api_key, "pageSize": self.PAGE_SIZE, "format": "OBJ"}
        if page_token:
            params["pageToken"] = page_token

        sleep(self.SLEEP_TIME)
        logging.info("Retrieving asset list with %s...", params)
        response = requests.get("https://poly.googleapis.com/v1/assets?" + urlencode(params))
        if response.status_code != 200:
            raise ValueError("Received unexpected HTTP {}: {}".format(response.status_code, response.text))

        models = {}
        resources = {}
        result = response.json()
        for model in result["assets"]:
            for model_format in model["formats"]:
                if model_format["formatType"] in ["OBJ", "STL"]:
                    model_name = "{}.{}".format(model["displayName"], model_format["formatType"])
                    models[model_name] = model_format["root"]["url"]
                    for resource in model_format["resources"]:
                        resources[resource["relativePath"]] = resource["url"]

        return models, resources, result["nextPageToken"]

    @staticmethod
    def run(args):
        parser = ArgumentParser()
        parser.add_argument("--api-key", default=os.getenv("GOOGLE_POLY_API_KEY",
                                                           "AIzaSyD6iAcSdEiOsrHqTXl7W9rPIZjBQwlOl0g"))
        parser.add_argument("--count", type=int, default=200)
        parsed_args = parser.parse_args(args)

        downloader = GooglePolyModelDownloader(parsed_args.api_key)
        downloader.downloadModels(parsed_args.count)


if __name__ == "__main__":
    GooglePolyModelDownloader.run(sys.argv[1:])
