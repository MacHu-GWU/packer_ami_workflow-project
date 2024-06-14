# -*- coding: utf-8 -*-

"""
AMI Builder automation.
"""

import typing as T
import json
import subprocess
import dataclasses
from functools import cached_property

import jinja2
import pynamodb_mate.api as pm
import aws_console_url.api as aws_console_url
import simple_aws_ec2.api as simple_aws_ec2
from pathlib_mate import Path
from dateutil.parser import parse

from .param import WorkflowParam, StepParam
from .workspace import Workspace
from .dynamodb import T_AMI_DATA
from .ec2 import tag_image, find_ami_by_name
from .logger import logger


def filter_packer_files(path: Path) -> bool:
    """
    Identify whether it is a ``.pkr.hcl`` or ``.pkrvars.hcl`` file.
    """
    return path.basename.endswith("pkr.hcl") or path.basename.endswith("pkrvars.hcl")


@dataclasses.dataclass
class AmiBuilder:
    """
    This class provide automation for building an AMI for a single step.

    :param workflow_param: The :class:`WorkflowParam` object.
    :param step_param: The :class:`StepParam` object.

    - :meth:`run_packer_build_workflow`
    - :meth:`tag_ami`
    - :meth:`create_dynamodb_item`
    - :meth:`delete_ami`
    """

    workflow_param: WorkflowParam = dataclasses.field()
    step_param: StepParam = dataclasses.field()
    workspace: Workspace = dataclasses.field()
    table_class: T.Type[T_AMI_DATA] = dataclasses.field()

    @cached_property
    def source_ami_id(self) -> str:
        """
        Get the source AMI id. If the step doesn't have previous step id,
        then this is the first step. So that the source AMI is the root base AMI.
        Otherwise, use DynamoDB to pull previous step AMI information.

        :return: the source ami id for this step.
        """
        if self.step_param.previous_step_id is None:  # use root base ami
            return self.workflow_param.root_base_ami_id
        else:
            image = self.table_class.get_image(
                workflow_id=self.workflow_param.workflow_id,
                step_id=self.step_param.previous_step_id,
            )
            return image.ami_id

    @cached_property
    def source_ami_name(self) -> str:
        """
        Get the source AMI name. If the step doesn't have previous step id,
        then this is the first step. So that the source AMI is the root base AMI.
        Otherwise, use DynamoDB to pull previous step AMI information.

        :return: the source ami name for this step.
        """
        if self.step_param.previous_step_id is None:  # use root base ami
            return self.workflow_param.root_base_ami_name
        else:
            image = self.table_class.get_image(
                workflow_id=self.workflow_param.workflow_id,
                step_id=self.step_param.previous_step_id,
            )
            return image.ami_name

    @cached_property
    def output_ami_name(self) -> str:
        """
        The output AMI name follows this naming convention
        ``{root_ami_name}/{workflow_id}/{step_id}``

        :return: the output ami name.
        """
        # figure out the output_ami_name
        if self.workflow_param.root_base_ami_name.endswith("/"):
            root_base_ami_name = self.workflow_param.root_base_ami_name[:-1]
        else:
            root_base_ami_name = self.workflow_param.root_base_ami_name
        output_ami_name = "/".join(
            [
                root_base_ami_name,
                self.workflow_param.workflow_id,
                self.step_param.step_id,
            ]
        )
        return output_ami_name

    @classmethod
    def make(
        cls,
        dir_step: Path,
        table_class: T.Type[T_AMI_DATA],
        workflow_param_class: T.Type[WorkflowParam] = WorkflowParam,
        step_param_class: T.Type[StepParam] = StepParam,
    ):
        """
        Factory method.

        :param table_class: :class:`~packer_ami_workflow.dynamodb.AmiData` or
            user defined subclass.
        """
        path_workflow_param = dir_step.parent.joinpath("workflow_param.json")
        path_step_param = dir_step.joinpath("step_param.json")
        workflow_param = workflow_param_class.from_json_file(path_workflow_param)
        step_param = step_param_class.from_json_file(path_step_param)
        workspace = Workspace(name=step_param.step_id, dir_root=dir_step)

        # Setup PynamoDB connection
        with workflow_param.bsm.awscli():
            table_class._connection = None
            table_class.Meta.region = workflow_param.aws_region
            connection = pm.Connection()
            table_class.create_table(wait=True)

        builder = cls(
            workflow_param=workflow_param,
            step_param=step_param,
            workspace=workspace,
            table_class=table_class,
        )
        return builder

    @logger.start_and_end(
        msg="Clean up existing .pkc.hcl and .pkrvars.hcl files",
    )
    def clean_up(self):
        """
        Delete existing .pkc.hcl and .pkrvars.hcl files in the workspace directory.
        """
        for path in self.workspace.dir_root.select_file(
            filters=filter_packer_files,
            recursive=False,
        ):
            logger.info(f"remove {path} ...")
            path.remove()

    @logger.start_and_end(
        msg="Render packer template files",
    )
    def render(
        self,
        clean_up: bool = True,
    ):
        """
        Generate all the packer template files in the workspace directory,
        by rendering the jinja2 template with the parameter object.

        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.
        """
        if clean_up:
            with logger.nested():
                self.clean_up()

        # render all the packer template files
        for path in self.workspace.dir_templates.select_file(
            filters=filter_packer_files,
            recursive=False,
        ):
            path_out = (
                self.workspace.dir_root / f"{self.step_param.step_id}{path.basename}"
            )
            logger.info(f"render {path_out} ...")
            path_out.write_text(jinja2.Template(path.read_text()).render(builder=self))

    @logger.start_and_end(
        msg="run packer validate",
    )
    def packer_validate(
        self,
        render: bool = True,
        clean_up: bool = True,
    ):
        """
        Run ``packer validate``.

        :param render: Whether to render the jinja2 template before running the command.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.

        Reference:

        - https://developer.hashicorp.com/packer/docs/commands/validate
        """
        if render:
            with logger.nested():
                self.render(clean_up=clean_up)

        args = ["packer", "validate"]
        for path in self.workspace.dir_root.select_file(
            filters=lambda p: p.basename.endswith(".pkrvars.hcl"),
            recursive=False,
        ):
            args.append(f"-var-file={path}")

        args.append(f"{self.workspace.dir_root}")

        logger.info("run 'packer validate' command:")
        logger.info("packer validate \\\n\t" + " \\\n\t".join(args[2:]))

        with self.workspace.dir_root.temp_cwd():
            subprocess.run(args, check=True)

    @logger.start_and_end(
        msg="run packer build",
    )
    def packer_build(
        self,
        render: bool = True,
        clean_up: bool = True,
        dry_run: bool = True,
    ):
        """
        Run ``packer build``.

        :param render: Whether to render the jinja2 template before running the command.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.
        """
        if render:
            with logger.nested():
                self.render(clean_up=clean_up)

        args = [
            "packer",
            "build",
            "-debug",
        ]

        for path in self.workspace.dir_root.select_file(
            filters=lambda p: p.basename.endswith(".pkrvars.hcl"),
            recursive=False,
        ):
            args.append(f"-var-file={path}")

        args.append(f"{self.workspace.dir_root}")

        logger.info("run 'packer build' command:")
        logger.info("packer build \\\n\t" + " \\\n\t".join(args[2:]))

        with self.workspace.dir_root.temp_cwd():
            if dry_run is False:
                subprocess.run(args, check=True)

    @logger.start_and_end(
        msg="run packer build workflow",
    )
    def run_packer_build_workflow(
        self,
        render: bool = True,
        clean_up: bool = True,
        validate: bool = True,
        dry_run: bool = True,
    ):
        """
        Run ``packer validate``.
        :param render: Whether to render the jinja2 template before running the command.
        :param clean_up: Whether to clean up the existing ``.pkr.hcl`` and ``.pkrvars.hcl`` files.
        :param validate: Whether to run the packer validate command before running the packer build command.
        :param dry_run: Whether to run the command in dry-run mode.
        """
        if render:
            with logger.nested():
                self.render(clean_up=clean_up)

        if validate:
            with logger.nested():
                self.packer_validate(render=False)

        with logger.nested():
            self.packer_build(render=False, clean_up=False, dry_run=dry_run)

    @logger.start_and_end(
        msg="create image manually",
    )
    def create_image_manually(
        self,
        instance_id: str,
        wait: bool = True,
        delays: T.Union[int, float] = 10,
        timeout: T.Union[int, float] = 300,
    ):
        # Ensure the ec2 instance is fully stopped before creating image
        response = self.workflow_param.bsm.ec2_client.describe_instances(
            InstanceIds=[instance_id]
        )
        instance_status = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        if instance_status != "stopped":
            raise ValueError(
                "You can only create image when instance is fully stopped!"
            )

        tags = self.get_ami_aws_tags()

        res = self.workflow_param.bsm.ec2_client.create_image(
            InstanceId=instance_id,
            Name=self.output_ami_name,
            TagSpecifications=[
                {
                    "ResourceType": "image",
                    "Tags": [{"Key": k, "Value": v} for k, v in tags.items()],
                }
            ],
        )
        image_id = res["ImageId"]

        url = self.workflow_param.aws_console.ec2.get_ami(image_id)
        logger.info(f"preview Image: {url}")

        if wait:
            logger.info("wait Image to reach available state")
            image = simple_aws_ec2.Image.from_id(
                ec2_client=self.workflow_param.bsm.ec2_client,
                image_id=image_id,
            )
            image.wait_for_available(
                ec2_client=self.workflow_param.bsm.ec2_client,
                delays=delays,
                timeout=timeout,
                verbose=True,
            )

    def get_ami_aws_tags(self) -> T.Dict[str, str]:
        tags = {
            "Name": self.output_ami_name,
            "packer:base_ami_id": self.source_ami_id,
            "packer:base_ami_name": self.source_ami_name,
            "packer:root_base_ami_id": self.workflow_param.root_base_ami_id,
            "packer:root_base_ami_name": self.workflow_param.root_base_ami_name,
        }
        tags.update(self.workflow_param.aws_tags)
        return tags

    @logger.start_and_end(
        msg="tag ami",
    )
    def tag_ami(self) -> str:
        tags = self.get_ami_aws_tags()
        ami_id = tag_image(
            ec2_client=self.workflow_param.bsm.ec2_client,
            image_name=self.output_ami_name,
            tags=tags,
        )
        logger.info("tags:")
        logger.info(json.dumps(tags, indent=4))
        return ami_id

    @logger.start_and_end(
        msg="create DynamoDB item for AMI",
    )
    def create_dynamodb_item(self) -> T_AMI_DATA:
        new_image = find_ami_by_name(
            ec2_client=self.workflow_param.bsm.ec2_client,
            ami_name=self.output_ami_name,
        )
        aws_console = aws_console_url.AWSConsole(
            aws_region=self.workflow_param.aws_region
        )
        url = aws_console.ec2.get_ami(image_id_or_arn=new_image.id)

        ami_data: T_AMI_DATA = self.table_class(
            workflow_id=self.workflow_param.workflow_id,
            step_id=self.step_param.step_id,
            ami_id=new_image.id,
            ami_name=self.output_ami_name,
            create_at=parse(new_image.creation_date),
            aws_console_url=url,
            base_ami_id=self.source_ami_id,
            base_ami_name=self.source_ami_name,
            root_base_ami_id=self.workflow_param.root_base_ami_id,
            root_base_ami_name=self.workflow_param.root_base_ami_name,
            details=dataclasses.asdict(new_image),
            metadata=self.step_param.metadata,
        )
        ami_data.save()
        logger.info(f"DynamoDB item details")
        logger.info(f"{ami_data.workflow_id = }")
        logger.info(f"{ami_data.step_id = }")
        logger.info(f"{ami_data.ami_id = }")
        logger.info(f"{ami_data.ami_name = }")
        logger.info(f"preview AMI: {ami_data.aws_console_url}")
        logger.info(f"preview DynamoDB item: {ami_data.item_detail_console_url}")
        return ami_data

    @logger.start_and_end(
        msg="delete AMI",
    )
    def delete_ami(
        self,
        delete_snapshot: bool = False,
        skip_prompt: bool = False,
    ):
        new_image = find_ami_by_name(
            ec2_client=self.workflow_param.bsm.ec2_client,
            ami_name=self.output_ami_name,
        )
        if new_image is None:
            raise ValueError(f"AMI {self.output_ami_name} not found.")

        logger.info(f"delete AMI {new_image.id}")
        if delete_snapshot:
            for snapshot_id in new_image.ebs_snapshot_id_list:
                logger.info(f"delete Snapshot {snapshot_id}")

        new_image.deregister(
            ec2_client=self.workflow_param.bsm.ec2_client,
            delete_snapshot=delete_snapshot,
            skip_prompt=skip_prompt,
        )
