# -*- coding: utf-8 -*-

from pathlib_mate import Path
import pynamodb_mate.api as pm
import awscli_mate.api as awscli_mate
from boto_session_manager import BotoSesManager

import acore_ami.api as acore_ami

# set the previous and this step id
previous_step_id = acore_ami.StepIdEnum.build_deps.value
this_step_id = acore_ami.StepIdEnum.server_data.value

dir_here = Path.dir_here(__file__)

# initialize your workspace object
# we set ``dir_root`` to the current directory
ws = acore_ami.Workspace(
    name="aws_ubuntu",
    dir_root=dir_here,
)

# initialize your workflow parameter object with values
# you may read sensitive data from external store, such as AWS SSM Parameter Store
path_workflow_param = dir_here.parent.joinpath("workflow_param.json")
workflow_param = acore_ami.WorkflowParam.from_json_file(path_workflow_param)

bsm = BotoSesManager(profile_name=workflow_param.aws_profile)
aws_cli_config = awscli_mate.AWSCliConfig()
aws_cli_config.set_profile_as_default(workflow_param.aws_profile)

# initialize your step parameter object with values
# you may read sensitive data from external store, such as AWS SSM Parameter Store
base_image = acore_ami.AmiData.get_one_or_none(
    workflow_param.workflow_id,
    previous_step_id,
)
source_ami_id = base_image.ami_id

step_param = acore_ami.StepParam(
    step_id=this_step_id,
    source_ami_id=source_ami_id,
    output_ami_name=(
        "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server"
        f"/{this_step_id}-{workflow_param.workflow_id}"
    ),
)

# ------------------------------------------------------------------------------
# run packer build
# ------------------------------------------------------------------------------
ws.run_packer_build_workflow(
    workflow_param=workflow_param,
    step_param=step_param,
    render=True,
    clean_up=True,
    validate=True,
    dry_run=True,  # True = NOTHING happen, False = run packer build
)

# ------------------------------------------------------------------------------
# Tag newly created AMI
# ------------------------------------------------------------------------------
tags = {
    "Name": step_param.output_ami_name,
}
tags.update(workflow_param.aws_tags)
ami_id = acore_ami.tag_image(
    ec2_client=bsm.ec2_client,
    image_name=step_param.output_ami_name,
    tags=tags,
)

# ------------------------------------------------------------------------------
# Create DynamoDB item for the new image
# ------------------------------------------------------------------------------
with bsm.awscli():
    pm.Connection()
    acore_ami.AmiData.create_table(wait=True)
    new_image = acore_ami.create_dynamodb_item_for_new_image(
        ec2_client=bsm.ec2_client,
        aws_region=bsm.aws_region,
        workflow_id=workflow_param.workflow_id,
        step_id=this_step_id,
        new_ami_name=step_param.output_ami_name,
        base_ami_id=base_image.ami_id,
        base_ami_name=base_image.ami_name,
        root_base_ami_id=workflow_param.root_base_ami_id,
        root_base_ami_name=workflow_param.root_base_ami_name,
        metadata={"key": "value"},
    )
