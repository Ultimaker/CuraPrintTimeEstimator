# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from urllib.parse import urlencode

import re
import requests
import shutil
from time import sleep
from typing import Dict

from Settings import Settings
from curaPrintTimeEstimator.CuraPrintTimeEstimator import CuraPrintTimeEstimator


class ThingiverseModelDownloader:
    """
    Class capable of downloading model files from Thingiverse.com.
    """

    SLEEP_TIME = 0.1  # 10 requests per second
    PAGE_SIZE = 30
    COUNT = 200
    SEARCH_TYPE = "popular"

    FILENAME_FILTER = re.compile(CuraPrintTimeEstimator.FILENAME_FILTER)

    PAGINATE_URL = "https://www.thingiverse.com/ajax/things/paginate"
    THING_FILES_URL = "https://www.thingiverse.com/thing:{}/files"
    DOWNLOAD_URL = "https://www.thingiverse.com/download:{}"

    def downloadModels(self) -> None:
        """
        Downloads the most popular Thingiverse models until the amount of models requested in self.COUNT is reached.
        """
        downloaded_count = len(os.listdir("./models/*.stl"))
        page_number = 1
        while downloaded_count < self.COUNT:
            for thing_name, thing_url in self._listThingUrls(page_number).items():
                for model_name, model_url in self._listThingFiles(thing_url).items():
                    self._download(model_name, model_url)
                    downloaded_count += 1
                    if downloaded_count == self.COUNT:
                        break
            page_number += 1

    def _download(self, name: str, url: str) -> None:
        """
        Downloads a model file with the given filename from the passed URL.
        :param name: The file name.
        :param url: The URL to download from.
        """
        file_name = "{}/models/{}".format(Settings.PROJECT_DIR, name)
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

    def _listThingUrls(self, page_number: int) -> Dict[str, str]:
        """
        Retrieves a list of the most popular things in Thingiverse.
        :param page_number: The page number, starting from 1.
        :return: A dict with the thing name as key and the file URL as value.
        """
        params = {"page": page_number, "type": self.SEARCH_TYPE, "per_page": self.PAGE_SIZE}

        sleep(self.SLEEP_TIME)
        logging.info("Retrieving %s models with %s...", self.SEARCH_TYPE, params)
        response = requests.get("{}?{}".format(self.PAGINATE_URL, urlencode(params)))
        if response.status_code != 200:
            raise ValueError("Received unexpected HTTP {}: {}".format(response.status_code, response.text))

        things = {}
        for thing_id, thing_name in re.findall(r'href="/thing:(\d+)">[^>]+>([^<]+)', response.text):
            things[thing_name.strip()] = self.THING_FILES_URL.format(thing_id)
        return things

    def _listThingFiles(self, thing_url) -> Dict[str, str]:
        """
        Finds a list of files for the given Thingiverse URL.
        :param thing_url: The URL to the 'thing' in Thingiverse.
        :return: A dict with the file name as key and the file URL as value.
        """
        sleep(self.SLEEP_TIME)
        response = requests.get(thing_url)
        files = {}
        for file_id, file_name in re.findall(r'href="/download:(\d+)" title="([^\"]+)"', response.text):
            if self.FILENAME_FILTER.match(file_name, re.IGNORECASE):
                files[file_name] = self.DOWNLOAD_URL.format(file_id)
        return files

    @staticmethod
    def run() -> None:
        """
        Instantiates the downloader and runs it.
        """
        downloader = ThingiverseModelDownloader()
        downloader.downloadModels()
