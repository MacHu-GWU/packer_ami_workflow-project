# -*- coding: utf-8 -*-

from pathlib_mate import Path
from packer_ami_workflow.tests.example import AmiBuilder

dir_here = Path.dir_here(__file__)
builder = AmiBuilder.make_builder(dir_step=dir_here)

# dry_run is True = NOTHING happen, False = run packer build
builder.create_image_manually(instance_id="i-a1b2c3d4")
builder.create_dynamodb_item()
# builder.delete_ami(delete_snapshot=False, skip_prompt=False)
