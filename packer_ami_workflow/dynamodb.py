# -*- coding: utf-8 -*-

"""
DynamoDB ORM layer.
"""

import typing as T
import dataclasses
import pynamodb_mate.api as pm


class StepIdIndex(pm.GlobalSecondaryIndex):
    """
    Step Id lookup Global secondary index.
    """

    class Meta:
        index_name = "step_id_index"
        projection = pm.AllProjection()

    step_id = pm.UnicodeAttribute(hash_key=True)
    create_at = pm.UTCDateTimeAttribute(range_key=True)


class AmiData(pm.Model):
    """
    This is the model class for the DynamoDB table for storing AMI metadata.

    :param workflow_id:
    :param step_id:
    :param ami_id: the AMI id.
    :param ami_name: the AMI name.
    :param create_at: when this AMI is created.
    :param aws_console_url: AWS console url to open the AMI details in the browser.
    :param base_ami_id: this AMI is built on top of which base AMI?
    :param base_ami_name: name of the base AMI.
    :param root_base_ami_id: which AMI we originally start from? Usually it's the
        ubuntu official AMI.
    :param root_base_ami_name: name of the root base AMI.
    :param details: the response of the
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html
        API call.
    :param metadata: user custom metadata
    """

    workflow_id = pm.UnicodeAttribute(hash_key=True)
    step_id = pm.UnicodeAttribute(range_key=True)
    ami_id = pm.UnicodeAttribute()
    ami_name = pm.UnicodeAttribute()
    create_at = pm.UTCDateTimeAttribute()
    aws_console_url = pm.UnicodeAttribute()
    base_ami_id = pm.UnicodeAttribute()
    base_ami_name = pm.UnicodeAttribute()
    root_base_ami_id = pm.UnicodeAttribute()
    root_base_ami_name = pm.UnicodeAttribute()
    details = pm.JSONAttribute()
    metadata = pm.JSONAttribute()

    step_id_index = StepIdIndex()

    @classmethod
    def get_image(cls, workflow_id: str, step_id: str):
        """
        Get the AMI data details.

        :param workflow_id: the workflow id.
        :param step_id: the step id.
        """
        return cls.get_one_or_none(workflow_id, step_id)

    @classmethod
    def query_by_workflow(cls, workflow_id: str):
        """
        Get all AMI (steps) data for a specific workflow.

        :param workflow_id: the workflow id.
        """
        return list(
            sorted(
                cls.query(hash_key=workflow_id),
                key=lambda x: x.create_at,
                reverse=True,
            )
        )

    @classmethod
    def query_by_step_id(cls, step_id: str):
        """
        Get all AMI versions (from different workflow) for a specific step.

        :param step_id: the step id.
        """
        return list(
            sorted(
                cls.step_id_index.query(hash_key=step_id),
                key=lambda x: x.create_at,
                reverse=True,
            )
        )


T_AMI_DATA = T.TypeVar("T_AMI_DATA", bound=AmiData)
