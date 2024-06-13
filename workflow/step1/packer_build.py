# -*- coding: utf-8 -*-

from pathlib_mate import Path
from packer_ami_workflow.tests.example import AmiBuilder

dir_here = Path.dir_here(__file__)
builder = AmiBuilder.make_builder(dir_step=dir_here)

# dry_run is True = NOTHING happen, False = run packer build
builder.run_packer_build_workflow(dry_run=False)
builder.tag_ami()
builder.create_dynamodb_item()
# builder.delete_ami(delete_snapshot=False, skip_prompt=False)
