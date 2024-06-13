# -*- coding: utf-8 -*-

"""
这个脚本能帮你找到合适的由 ubuntu 官方提供的 AWS AMI 作为 base image. 一旦找到之后,
就可以将 id 和 name 填入 ``workflow_param.json`` 文件中了.

你可以参考 ubuntu 官方的
`Find Ubuntu images on AWS <https://documentation.ubuntu.com/aws/en/latest/aws-how-to/instances/find-ubuntu-images/>`_
文档来了解具体方法. 本脚本只是自动化了这个方法的.

下面是我在 2024-06-13 从上面的文档中找到的一些信息, 我自己留个档:

The format for the parameter is:

    ubuntu/$PRODUCT/$RELEASE/stable/current/$ARCH/$VIRT_TYPE/$VOL_TYPE/ami-id

- PRODUCT: server, server-minimal or pro-server
- RELEASE: jammy, 22.04, focal, 20.04, bionic, 18.04, xenial, or 16.04
- ARCH: amd64 or arm64
- VIRT_TYPE: pv or hvm
- VOL_TYPE: ebs-gp3 (for >=23.10), ebs-gp2 (for <=23.04), ebs-io1, ebs-standard, or instance-store
"""

from pathlib_mate import Path
from boto_session_manager import BotoSesManager
from rich import print as rprint

import packer_ami_workflow.api as paw

# ------------------------------------------------------------------------------
# 根据 ubuntu 的版本, 以及 arch (AMD64 还是 ARM) 来找到合适的 root base ami
# 其中 owner_account_id 来自于本脚本最前面的 reference 文档
aws_profile = "bmt_app_dev_us_east_1"
root_base_ami_name = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
root_base_ami_owner_account_id = "099720109477"
# ------------------------------------------------------------------------------
bsm = BotoSesManager(profile_name=aws_profile)

# locate the latest root base ami, this is my own implementation of the
# packer's source_ami_filter feature, for better control
images = paw.find_root_base_ami(
    ec2_client=bsm.ec2_client,
    source_ami_name=root_base_ami_name,
    source_ami_owner_account_id=root_base_ami_owner_account_id,
)
latest_root_base_ami = images[0]
ami_catalog_url = (
    f"https://{bsm.aws_region}.console.aws.amazon.com/ec2"
    f"/home?region={bsm.aws_region}#AMICatalog:"
)
print("Root base AMI details:")
rprint(latest_root_base_ami)
print(f"Root base AMI id = {latest_root_base_ami.id}")
print(f"Root base AMI name = {latest_root_base_ami.name}")
print(
    f"Enter the AMI id in ami catalog url to see the details "
    f"(in Community AMIs tab): {ami_catalog_url}"
)
