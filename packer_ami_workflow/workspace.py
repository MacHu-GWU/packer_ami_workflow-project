# -*- coding: utf-8 -*-

import dataclasses

from pathlib_mate import Path


def filter_packer_files(path: Path) -> bool:
    """
    Identify whether it is a ``.pkr.hcl`` or ``.pkrvars.hcl`` file.
    """
    return path.basename.endswith("pkr.hcl") or path.basename.endswith("pkrvars.hcl")


@dataclasses.dataclass
class Workspace:
    """
    :param name: The name of the workspace. This is the prefix of all HCL file.
    :param dir_root: The root directory of the workspace.

    The workspace has to follow the following directory structure::

        /workflow/
        /workflow/find_root_base_image_id.py
        /workflow/workflow_param.json
        /workflow/step1/
        /workflow/step1/templates/
        /workflow/step1/templates/.pkr.hcl
        /workflow/step1/templates/.pkrvars.hcl
        /workflow/step1/templates/.variables.pkr.hcl
        /workflow/step1/.gitignore
        /workflow/step1/packer_build.py
    """

    name: str = dataclasses.field()
    dir_root: Path = dataclasses.field()

    @property
    def dir_templates(self) -> Path:
        """
        This is the directory where all the packer template source code are stored.
        """
        return self.dir_root / "templates"

    @property
    def path_pkr_hcl_tpl(self) -> Path:
        """
        The path to the .pkr.hcl jinja2 template file.
        """
        return self.dir_templates / f".pkr.hcl"

    @property
    def path_pkrvars_hcl_tpl(self) -> Path:
        """
        The path to the .pkrvars.hcl  jinja2 template file.
        """
        return self.dir_templates / f".pkrvars.hcl"

    @property
    def path_variables_pkr_hcl_tpl(self) -> Path:
        """
        The path to the .variables.pkr.hcl  jinja2 template file.
        """
        return self.dir_templates / f".variables.pkr.hcl"

    @property
    def path_pkr_hcl(self) -> Path:
        """
        The path to the rendered .pkr.hcl file.
        """
        return self.dir_root / f"{self.name}.pkr.hcl"

    @property
    def path_pkrvars_hcl(self) -> Path:
        """
        The path to the rendered .pkrvars.hcl file.
        """
        return self.dir_root / f"{self.name}.pkrvars.hcl"

    @property
    def path_variables_pkr_hcl(self) -> Path:
        """
        The path to the rendered .variables.pkr.hcl file.
        """
        return self.dir_root / f"{self.name}.variables.pkr.hcl"
