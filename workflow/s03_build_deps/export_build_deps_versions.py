#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script export the build dependencies version to a json file
"""

import json
import subprocess
from pathlib_mate import Path

dir_home = Path.home()
path_build_deps_versions_json = dir_home / "build-deps-versions.json"

build_deps_versions = {}

response = subprocess.run(["lsb_release", "-a"], capture_output=True, check=True)
build_deps_versions["ubuntu"] = response.stdout.decode("utf-8").strip()

response = subprocess.run(["openssl", "version"], capture_output=True, check=True)
build_deps_versions["openssl"] = response.stdout.decode("utf-8").strip()

response = subprocess.run(["clang", "--version"], capture_output=True, check=True)
build_deps_versions["clang"] = response.stdout.decode("utf-8").strip()

response = subprocess.run(["mysql", "--version"], capture_output=True, check=True)
build_deps_versions["mysql"] = response.stdout.decode("utf-8").strip()

response = subprocess.run(["screen", "--version"], capture_output=True, check=True)
build_deps_versions["screen"] = response.stdout.decode("utf-8").strip()

response = subprocess.run(["clang", "--version"], capture_output=True, check=True)
build_deps_versions["ubuntu"] = response.stdout.decode("utf-8").strip()

path_build_deps_versions_json.write_text(json.dumps(build_deps_versions, indent=4))
