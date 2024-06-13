# -*- coding: utf-8 -*-

"""
Please read the README.rst file before you read this file.
"""

from pathlib_mate import Path
import pynamodb_mate.api as pm
from boto_session_manager import BotoSesManager
import aws_console_url.api as aws_console_url

import acore_ami.api as acore_ami

# ------------------------------------------------------------------------------
# NOTE: update these value before you run this script
instance_id = "i-0f65b9c69fd65142e"
mysql_version = "8.0.28"
previous_step_id = acore_ami.StepIdEnum.pyenv.value
this_step_id = acore_ami.StepIdEnum.mysql.value
# ------------------------------------------------------------------------------

dir_here = Path.dir_here(__file__)
path_workflow_param = dir_here.parent.joinpath("workflow_param.json")
workflow_param = acore_ami.WorkflowParam.from_json_file(path_workflow_param)
bsm = BotoSesManager(profile_name=workflow_param.aws_profile)
aws_console = aws_console_url.AWSConsole.from_bsm(bsm)

# Ensure the ec2 instance is fully stopped before creating image
response = bsm.ec2_client.describe_instances(InstanceIds=[instance_id])
instance_status = response["Reservations"][0]["Instances"][0]["State"]["Name"]
if instance_status != "stopped":
    raise ValueError("You can only create image when instance is fully stopped!")

new_image_name = (
    "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server"
    f"/{this_step_id}-{workflow_param.workflow_id}"
)


def create_image():
    tags = {
        "Name": new_image_name,
    }
    tags.update(workflow_param.aws_tags)

    res = bsm.ec2_client.create_image(
        InstanceId=instance_id,
        Name=new_image_name,
        TagSpecifications=[
            {
                "ResourceType": "image",
                "Tags": [{"Key": k, "Value": v} for k, v in tags.items()],
            }
        ],
    )
    image_id = res["ImageId"]
    url = aws_console.ec2.get_ami(image_id)
    print(f"preview Image: {url}")


def create_dynamodb_item():
    with bsm.awscli():
        pm.Connection()
        acore_ami.AmiData.create_table(wait=True)
        base_image = acore_ami.AmiData.iter_query(
            workflow_param.workflow_id,
            acore_ami.AmiData.step_id == previous_step_id,
        ).one()

        new_image = acore_ami.create_dynamodb_item_for_new_image(
            ec2_client=bsm.ec2_client,
            aws_region=bsm.aws_region,
            workflow_id=workflow_param.workflow_id,
            step_id=this_step_id,
            new_ami_name=new_image_name,
            base_ami_id=base_image.ami_id,
            base_ami_name=base_image.ami_name,
            root_base_ami_id=workflow_param.root_base_ami_id,
            root_base_ami_name=workflow_param.root_base_ami_name,
            metadata={
                "description": f"ubuntu20 with mysql {mysql_version}",
            },
        )


create_image()
# you need to wait the image is created before you run create_dynamodb_item()
# create_dynamodb_item()
