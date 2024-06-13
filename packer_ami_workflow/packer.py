# -*- coding: utf-8 -*-

"""
Packer CLI related helpers.
"""

import typing as T
import os
import sys
import enum
import shutil
import subprocess
import contextlib
import dataclasses
from pathlib import Path


class OSEnum(str, enum.Enum):
    windows = "windows"
    macOS = "darwin"
    linux = "linux"
    freebsd = "freebsd"
    netbsd = "netbsd"
    openbsd = "openbsd"
    solaris = "solaris"


class ArchEnum(str, enum.Enum):
    a386 = "386"
    amd64 = "amd64"
    arm64 = "arm64"
    arm = "arm"
    ppc64le = "ppc64le"


class PlatformEnum(str, enum.Enum):
    windows_386 = f"{OSEnum.windows.value}_{ArchEnum.a386.value}"
    windows_amd64 = f"{OSEnum.windows.value}_{ArchEnum.amd64.value}"
    macOS_amd64 = f"{OSEnum.macOS.value}_{ArchEnum.amd64.value}"
    macOS_arm64 = f"{OSEnum.macOS.value}_{ArchEnum.arm64.value}"
    linux_386 = f"{OSEnum.linux.value}_{ArchEnum.a386.value}"
    linux_amd64 = f"{OSEnum.linux.value}_{ArchEnum.amd64.value}"
    linux_arm = f"{OSEnum.linux.value}_{ArchEnum.arm.value}"
    linux_arm64 = f"{OSEnum.linux.value}_{ArchEnum.arm64.value}"
    linux_ppc64le = f"{OSEnum.linux.value}_{ArchEnum.ppc64le.value}"
    freebsd_386 = f"{OSEnum.freebsd.value}_{ArchEnum.a386.value}"
    freebsd_amd64 = f"{OSEnum.freebsd.value}_{ArchEnum.amd64.value}"
    freebsd_arm = f"{OSEnum.freebsd.value}_{ArchEnum.arm.value}"
    netbsd_386 = f"{OSEnum.netbsd.value}_{ArchEnum.a386.value}"
    netbsd_amd64 = f"{OSEnum.netbsd.value}_{ArchEnum.amd64.value}"
    netbsd_arm = f"{OSEnum.netbsd.value}_{ArchEnum.arm.value}"
    openbsd_386 = f"{OSEnum.openbsd.value}_{ArchEnum.a386.value}"
    openbsd_amd64 = f"{OSEnum.openbsd.value}_{ArchEnum.amd64.value}"
    openbsd_arm = f"{OSEnum.openbsd.value}_{ArchEnum.arm.value}"
    solaris_amd64 = f"{OSEnum.solaris.value}_{ArchEnum.amd64.value}"


def build_packer_download_url(version: str, platform: PlatformEnum) -> str:
    return f"https://releases.hashicorp.com/packer/{version}/packer_{version}_{platform.value}.zip"


@contextlib.contextmanager
def temp_cwd(path: T.Union[str, Path]):
    """
    Temporarily set the current working directory (CWD) and automatically
    switch back when it's done.

    Example:

    .. code-block:: python

        with temp_cwd(Path("/path/to/target/working/directory")):
            # do something
    """
    path = Path(path).absolute()
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a dir!")
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(cwd)


@dataclasses.dataclass
class PackerInstaller:
    """
    An installer to install Packer on MacOS or Linux.

    Reference:

    - `Install Packer <https://developer.hashicorp.com/packer/install>`_: 官方安装文档
    - `Packer Releases <https://releases.hashicorp.com/packer>`_: Packer 的所有历史版本的
        pre-compiled binary 的下载地址. 同时也可以查到所有历史版本.
    - `Packer change log <https://github.com/hashicorp/packer/blob/main/CHANGELOG.md>`_:
        Packer 的所有版本的变更日志.

    :param version: The version of Packer to install. For example, "1.11.0".
    :param platform: The platform to install Packer on. For example, "PlatformEnum.linux_amd64".
    :param dir_workspace: The working directory for this installation task.

    Usage example:

    .. code-block:: python

        from pathlib import Path
        import packer_ami_workflow.api as paw

        packer_installer = paw.PackerInstaller(
            version="1.11.0",
            platform=paw.PlatformEnum.macOS_arm64,
            # platform=paw.PlatformEnum.linux_amd64,
            dir_workspace=Path(__file__).absolute().parent,
        )
        packer_installer.install()
    """

    version: str = dataclasses.field()
    platform: PlatformEnum = dataclasses.field()
    dir_workspace: Path = dataclasses.field()

    @property
    def dir_tmp(self) -> Path:
        """
        A temporary directory to store the downloaded zip file and the unzipped binary.
        """
        return self.dir_workspace.joinpath("tmp")

    def reset_temp_dir(self):
        if self.dir_tmp.exists():
            shutil.rmtree(self.dir_tmp)
        self.dir_tmp.mkdir()

    @property
    def download_url(self) -> str:
        return build_packer_download_url(self.version, self.platform)

    @property
    def path_packer_zip(self) -> Path:
        return self.dir_tmp.joinpath(self.download_url.split("/")[-1])

    @property
    def path_packer_binary(self) -> Path:
        return self.dir_tmp.joinpath("packer")

    def download(self):
        if not self.path_packer_zip.exists():
            args = [
                "wget",
                "-O",
                f"{self.path_packer_zip}",
                self.download_url,
            ]
            subprocess.run(args, check=True)

    def unzip(self):
        if self.path_packer_binary.exists():
            self.path_packer_binary.unlink()

        with temp_cwd(self.dir_tmp):
            args = ["unzip", f"{self.path_packer_zip}"]
            subprocess.run(args, check=True)

    def move_to_usr_local_bin(self):
        """
        Copy the pre-compiled binary to ``/usr/local/bin/packer``.

        - read this link to know more about /usr/local/bin folder: https://iboysoft.com/wiki/macos-usr-local-bin.html
        """
        dir_usr_local_bin = Path("/usr/local/bin")
        path_urs_local_bin_packer = dir_usr_local_bin.joinpath("packer")
        args = ["sudo", "mv", f"{self.path_packer_binary}", f"{dir_usr_local_bin}"]
        cmd = " ".join(args)

        if sys.platform == "darwin":
            print(
                "run this command in your terminal to copy packer "
                "to your /usr/local/bin folder, this cannot be done on MacOS"
            )
            print(cmd)
        elif sys.platform == "linux":
            print(f"Run: {cmd}")
            if path_urs_local_bin_packer.exists():
                path_urs_local_bin_packer.unlink()
            subprocess.run(args, check=True)
        else:
            raise NotImplementedError

        print("Now you can run this command to verify installation ")
        print("packer --version")

    def install(self):
        """
        Install packer pre-compiled binary.
        """
        self.reset_temp_dir()
        self.download()
        self.unzip()
        self.move_to_usr_local_bin()
