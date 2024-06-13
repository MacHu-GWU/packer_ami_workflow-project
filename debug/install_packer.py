# -*- coding: utf-8 -*-

from pathlib import Path
import packer_ami_workflow.api as paw

packer_installer = paw.PackerInstaller(
    version="1.11.0",
    platform=paw.PlatformEnum.macOS_arm64,
    # platform=paw.PlatformEnum.linux_amd64,
    dir_workspace=Path(__file__).absolute().parent,
)
packer_installer.install()
