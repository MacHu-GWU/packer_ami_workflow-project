#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script download azerothcore server data (map data)
"""

import typing as T
import os
import json
import subprocess
from datetime import datetime, timezone
from pathlib_mate import Path

dir_home = Path.home()
path_server_source_code_metadata = dir_home / "server_source_code_metadata.json"

dir_git_repos = dir_home / "git_repos"

# ${HOME}/azeroth-server-data
dir_azeroth_server_data = dir_home / "azeroth-server-data"
# ${HOME}/azeroth-server-data/metadata.json
path_azeroth_server_data_metadata_json = dir_azeroth_server_data / "metadata.json"
# ${HOME}/azeroth-server-data/data.zip
path_azeroth_server_data_zip = dir_azeroth_server_data / "data.zip"

# ${HOME}/azeroth-server
dir_azeroth_server = dir_home / "azeroth-server"
# ${HOME}/azeroth-server/etc/authserver.conf.dist
path_azeroth_server_authserver_conf_dist = (
    dir_azeroth_server / "etc" / "authserver.conf.dist"
)
# ${HOME}/azeroth-server/etc/worldserver.conf.dist
path_azeroth_server_worldserver_conf_dist = (
    dir_azeroth_server / "etc" / "worldserver.conf.dist"
)
# ${HOME}/azeroth-server/etc/authserver.conf
path_azeroth_server_authserver_conf = dir_azeroth_server / "etc" / "authserver.conf"
# ${HOME}/azeroth-server/etc/worldserver.conf
path_azeroth_server_worldserver_conf = dir_azeroth_server / "etc" / "worldserver.conf"

# Build Server related
# ${HOME}/git_repos/azerothcore-wotlk
dir_acore_repo = dir_git_repos / "azerothcore-wotlk"
# ${HOME}/git_repos/azerothcore-wotlk/modules
dir_modules = dir_acore_repo / "modules"
# ${HOME}/git_repos/azerothcore-wotlk/modules/mod-eluna
dir_mod_eluna_repo = dir_modules / "mod-eluna"
# ${HOME}/git_repos/azerothcore-wotlk/build
dir_build = dir_acore_repo / "build"


def clone_or_update_repo(
    git_url: str,
    dir_repo: Path,
    branch: str,
    is_single_branch: bool = False,
    depth: T.Optional[int] = None,
):
    """
    Git clone a repo to target location. If the repo already exists, git pull
    the latest code.

    This only works for public GitHub repo.

    :param git_url:
    :param dir_repo: the remote git repo folder will become this folder
    :param branch:
    :param is_single_branch:
    :param depth:
    """
    dir_repo.parent.mkdir_if_not_exists()
    if not dir_repo.exists():
        with dir_repo.parent.temp_cwd():
            args = [
                "git",
                "clone",
                git_url,
                "--branch",
                branch,
            ]
            if is_single_branch:
                args.append("--single-branch")
            if depth:
                args.extend(["--depth", f"{depth}"])
            args.append(dir_repo.abspath)
            subprocess.run(args)
    else:
        with dir_repo.temp_cwd():
            subprocess.run(["git", "pull"])


def get_commit_id(dir_repo: Path) -> str:
    """
    Get the current git commit id of a repo.
    """
    with dir_repo.temp_cwd():
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
        commit_id = res.stdout.decode("utf-8").strip()
        return commit_id


def utc_now() -> datetime:
    """
    Get timezone aware UTC now datetime object.
    """
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def utc_now_timestamp_suffix() -> str:
    """
    Return a string representing the UTC now datetime (up to second).
    Usually, this string is part of naming convention
    """
    now = utc_now()
    return now.strftime("%Y-%m-%d-%H-%M-%S")


def clone_azerothcore_wotlk():
    """
    "Clone" or "Update" the https://github.com/azerothcore/azerothcore-wotlk
    from GitHub. If the folder doesn't exist on local, then ``git clone``. If
    it already exists, then ``git pull``.
    """
    dir_git_repos.mkdir_if_not_exists()
    if dir_acore_repo.exists() is False:
        clone_or_update_repo(
            git_url="https://github.com/azerothcore/azerothcore-wotlk.git",
            dir_repo=dir_acore_repo,
            branch="master",
            is_single_branch=True,
            depth=1,
        )


def build_core():
    """
    Build server core.
    """
    # backup existing build
    if dir_azeroth_server.exists():
        backup_suffix = utc_now_timestamp_suffix()
        dir_azeroth_server_backup = dir_azeroth_server.change(
            new_basename=dir_azeroth_server.basename + f"-{backup_suffix}"
        )
        subprocess.run(["mv", dir_azeroth_server, dir_azeroth_server_backup])

    if dir_build.exists():
        dir_build.remove_if_exists()

    dir_build.mkdir_if_not_exists()
    with dir_build.temp_cwd():
        subprocess.run(
            [
                "cmake",
                "../",
                f"-DCMAKE_INSTALL_PREFIX={dir_azeroth_server.abspath}/",
                "-DCMAKE_C_COMPILER=/usr/bin/clang",
                "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
                "-DWITH_WARNINGS=1",
                "-DTOOLS=0",
                "-DSCRIPTS=static",
                "-DMODULES=static",
            ]
        )
        n_cpu = os.cpu_count()
        subprocess.run(
            [
                "make",
                "-j",
                f"{n_cpu}",
            ]
        )
        subprocess.run(
            [
                "make",
                "install",
            ]
        )

def clone_azerothcore_mod_eluna():
    """
    "Clone" or "Update" the mod-eluna source code.
    Reference:
    - https://www.azerothcore.org/catalogue.html#/details/413964782
    - https://github.com/azerothcore/mod-eluna
    """
    dir_git_repos.mkdir_if_not_exists()
    if dir_mod_eluna_repo.exists() is False:
        clone_or_update_repo(
            git_url="https://github.com/azerothcore/mod-eluna.git",
            dir_repo=dir_mod_eluna_repo,
            branch="master",
            is_single_branch=True,
            depth=1,
        )


def build():
    print("---------- Step 1. Clone https://github.com/azerothcore/azerothcore-wotlk")
    clone_azerothcore_wotlk()

    print("---------- Step 2. Clone additional modules")
    print("---------- Step 21. Clone https://github.com/azerothcore/mod-eluna")
    clone_azerothcore_mod_eluna()

    print("---------- Step 3. Build Core")
    build_core()

    print("---------- Step 4. Post Build")
    print("---------- Step 41. write metadata of the source code to a json file")
    metadata = {
        "azerothcore-wotlk": {
            "commit_id": get_commit_id(dir_acore_repo),
        },
        "mod-eluna": {
            "commit_id": get_commit_id(dir_mod_eluna_repo),
        },
    }
    print(f"metadata = {metadata}")
    path_server_source_code_metadata.write_text(json.dumps(metadata, indent=4))

    print("---------- Step 42. delete the generated build folder")
    dir_build.remove_if_exists()


if __name__ == "__main__":
    build()
