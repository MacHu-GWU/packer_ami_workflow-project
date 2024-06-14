# -*- coding: utf-8 -*-

from pathlib_mate import Path
from packer_ami_workflow.tests.example import AmiBuilder

dir_here = Path.dir_here(__file__)
builder = AmiBuilder.make_builder(dir_step=dir_here)

# ------------------------------------------------------------------------------
# Use this to create a new AMI image if using packer build
#   dry_run = True: NOTHING happen, dry_run = False: run packer build
# ------------------------------------------------------------------------------
# builder.run_packer_build_workflow(dry_run=True)
# builder.tag_ami()
# ------------------------------------------------------------------------------
# Use this to create a new AMI image from a stopped EC2 instance
#   instance_id: the EC2 instance id
# ------------------------------------------------------------------------------
builder.create_image_manually(instance_id="i-1a2b3c", wait=True)
# ------------------------------------------------------------------------------
# Create a new item in the DynamoDB table
# ------------------------------------------------------------------------------
builder.create_dynamodb_item()
# ------------------------------------------------------------------------------
# Deregister the AMI image and delete the associated snapshot (optional)
# ------------------------------------------------------------------------------
# builder.delete_ami(delete_snapshot=False, skip_prompt=False)
