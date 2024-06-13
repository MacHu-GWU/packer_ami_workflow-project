# -*- coding: utf-8 -*-

from pathlib import Path
import packer_ami_workflow.api as paw

installer = paw.PackerInstaller(
    version="1.11.0",
    platform=paw.PlatformEnum.macOS_arm64,
    # platform=paw.PlatformEnum.linux_amd64,
    dir_workspace=Path(__file__).absolute().parent,
)
installer.install()
