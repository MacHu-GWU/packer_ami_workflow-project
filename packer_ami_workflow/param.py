# -*- coding: utf-8 -*-

"""
The workflow and step level parameter system.
"""

import typing as T
import dataclasses
from functools import cached_property

from pathlib_mate import Path
from boto_session_manager import BotoSesManager
import aws_console_url.api as aws_console_url
from .vendor.jsonutils import json_loads


@dataclasses.dataclass
class BaseParam:
    @classmethod
    def from_json_file(cls, path):
        """
        Load the parameter object from a json file.
        """
        data = json_loads(text=Path(path).read_text())
        return cls(**data)


T_PARAM = T.TypeVar("T_PARAM", bound=BaseParam)


@dataclasses.dataclass
class WorkflowParam(BaseParam):
    """
    The workflow level parameter object. The parameters here are common values
    for all steps.

    :param workflow_id:
    :param aws_profile: The AWS profile name to use.
    :param aws_tags: The AWS tags to apply to the AMI.
    :param vpc_name: The VPC name where the packer build will run.
    :param is_default_vpc: are we using default VPC? use false or true (string, not boolean).
    :param subnet_name: The Subnet name where the packer build will run.
    :param security_group_name: The Security name where the packer build will use.
    :param ec2_iam_role_name: The IAM role name that the packer build will use.
    :param root_base_ami_name: The name of the root base AMI to use for building this AMI.
        this is only used in step 1.
    :param root_base_ami_owner_account_id: The owner account id of the root base AMI.
    """

    workflow_id: str = dataclasses.field()
    vpc_name: str = dataclasses.field()
    is_default_vpc: str = dataclasses.field()
    subnet_name: str = dataclasses.field()
    security_group_name: str = dataclasses.field()
    ec2_iam_role_name: str = dataclasses.field()
    root_base_ami_id: str = dataclasses.field()
    root_base_ami_name: str = dataclasses.field()
    profile_name: T.Optional[str] = dataclasses.field(default=None)
    region_name: T.Optional[str] = dataclasses.field(default=None)
    aws_access_key_id: T.Optional[str] = dataclasses.field(default=None)
    aws_secret_access_key: T.Optional[str] = dataclasses.field(default=None)
    aws_session_token: T.Optional[str] = dataclasses.field(default=None)
    aws_tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)

    @cached_property
    def bsm(self) -> BotoSesManager:
        kwargs = dict(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region_name,
            profile_name=self.profile_name,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return BotoSesManager(**kwargs)

    @cached_property
    def aws_region(self) -> str:
        return self.bsm.aws_region

    @cached_property
    def aws_console(self) -> aws_console_url.AWSConsole:
        return aws_console_url.AWSConsole.from_bsm(self.bsm)


@dataclasses.dataclass
class StepParam(BaseParam):
    """
    The step level parameter object. The parameters here are specific to each step.

    :param step_id: The step id.
    :param source_ami_id: The source AMI id to use for building this AMI.
    :param metadata: additional metadata for this step AMI.
    """

    step_id: str = dataclasses.field()
    previous_step_id: T.Optional[str] = dataclasses.field()
    metadata: T.Dict[str, str] = dataclasses.field(default_factory=dict)
