# -*- coding: utf-8 -*-

import dataclasses
from pathlib_mate import Path
import pynamodb_mate.api as pm

import packer_ami_workflow.api as paw


@dataclasses.dataclass
class WorkflowParam(paw.WorkflowParam):
    pass


@dataclasses.dataclass
class StepParam(paw.StepParam):
    pass


class AmiData(paw.AmiData):
    class Meta:
        table_name = "packer_ami_workflow_example"
        billing_mode = pm.constants.PAY_PER_REQUEST_BILLING_MODE


class AmiBuilder(paw.AmiBuilder):
    @classmethod
    def make_builder(
        cls,
        dir_step: Path,
    ):
        return cls.make(
            dir_step=dir_step,
            table_class=AmiData,
            workflow_param_class=WorkflowParam,
            step_param_class=StepParam,
        )
