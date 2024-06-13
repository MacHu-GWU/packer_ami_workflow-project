#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script download azerothcore server data (map data)
"""

import json
import subprocess
from datetime import date
from pathlib_mate import Path

dir_home = Path.home()
dir_azeroth_server_data = dir_home / "azeroth-server-data"
path_azeroth_server_data_metadata_json = dir_azeroth_server_data / "metadata.json"
path_azeroth_server_data_zip = dir_azeroth_server_data / "data.zip"

dir_azeroth_server_data.mkdir(parents=True, exist_ok=True)

# this data file will be periodically updated, so update the url when needed
download_url = "https://github.com/wowgaming/client-data/releases/download/v16/data.zip"

with dir_azeroth_server_data.temp_cwd():
    # download data.zip
    args = ["wget", download_url]
    subprocess.run(args, check=True)

    # unzip
    args = [
        "unzip",
        "data.zip",
    ]
    subprocess.run(args, check=True)

    # delete the data.zip to save disk
    path_azeroth_server_data_zip.remove_if_exists()

    # write metadata
    metadata = {
        "download_url": download_url,
        "download_date": str(date.today()),
    }
    path_azeroth_server_data_metadata_json.write_text(json.dumps(metadata, indent=4))
