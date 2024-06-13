# -*- coding: utf-8 -*-

from packer_ami_workflow import api


def test():
    _ = api
    _ = api.BaseParam
    _ = api.T_PARAM
    _ = api.WorkflowParam
    _ = api.StepParam
    _ = api.PlatformEnum
    _ = api.PackerInstaller
    _ = api.Workspace
    _ = api.StepIdIndex
    _ = api.AmiData
    _ = api.T_AMI_DATA
    _ = api.extract_essential_attributes_from_image_list
    _ = api.find_root_base_ami
    _ = api.find_ami_by_name
    _ = api.tag_image
    _ = api.AmiBuilder


if __name__ == "__main__":
    from packer_ami_workflow.tests import run_cov_test

    run_cov_test(__file__, "packer_ami_workflow.api", preview=False)
