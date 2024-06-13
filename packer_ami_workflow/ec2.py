# -*- coding: utf-8 -*-

"""
boto3 EC2 API utilities.
"""

import typing as T

import simple_aws_ec2.api as simple_aws_ec2

if T.TYPE_CHECKING:  # pragma: no cover
    # do: pip install "boto3_stubs[ec2]"
    from mypy_boto3_ec2.client import EC2Client


def extract_essential_attributes_from_image_list(
    images: T.List[simple_aws_ec2.Image],
) -> T.List[T.Dict[str, T.Any]]:
    """
    The original ``simple_aws_ec2.Image`` object has too many attributes,
    this function can extract important attributes only for print.
    """
    records = [
        dict(
            id=image.id,
            name=image.name,
            state=image.state,
            creation_date=image.creation_date,
            deprecation_time=image.deprecation_time,
        )
        for image in images
    ]
    return records


def find_root_base_ami(
    ec2_client: "EC2Client",
    source_ami_name: str,
    source_ami_owner_account_id: str,
) -> T.List[simple_aws_ec2.Image]:
    """
    This is the alternative of
    `source_ami_filter <https://developer.hashicorp.com/packer/integrations/hashicorp/amazon/latest/components/builder/ebs>`_
    feature in packer.

    It finds the root base ami by name and owner account id.
    """
    iter_proxy = simple_aws_ec2.Image.query(
        ec2_client=ec2_client,
        executable_users=["all"],
        filters=[
            dict(Name="owner-id", Values=[source_ami_owner_account_id]),
            dict(Name="name", Values=[source_ami_name]),
            # we use x86_64 only in this project
            dict(Name="architecture", Values=["x86_64"]),
            dict(Name="state", Values=["available"]),
            dict(Name="root-device-type", Values=["ebs"]),
            dict(Name="virtualization-type", Values=["hvm"]),
        ],
    )
    images = list()
    for image in iter_proxy:
        images.append(image)
    # sort images, latest image first
    images = list(sorted(images, key=lambda x: x.creation_date, reverse=True))
    return images


def find_ami_by_name(
    ec2_client: "EC2Client",
    ami_name: str,
) -> simple_aws_ec2.Image:
    """
    Find AMI object by its name. Since the ID is a generated value that we
    don't know, we usually locate AMI by name. In AMI project, we usually
    own these AMIs.

    :param ec2_client:
    :param ami_name: this is the Name parameter you pass to the
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/create_image.html
        API when creating image. It is not the name tag.
    """
    image = simple_aws_ec2.Image.query(
        ec2_client=ec2_client,
        filters=[
            dict(Name="name", Values=[ami_name]),
        ],
    ).one()
    return image


def tag_image(
    ec2_client: "EC2Client",
    image_name: str,
    tags: T.Optional[T.Dict[str, str]] = None,
) -> str:
    """
    Tag the image with the given name.

    :param bsm: BotoSesManager
    :param image_name: The unique name of the image that can be used to locate the ami id
    :param tags: The tags to apply to the image.
    """
    # find image id
    image = simple_aws_ec2.Image.query(
        ec2_client=ec2_client,
        filters=[
            dict(Name="name", Values=[image_name]),
            dict(Name="state", Values=[simple_aws_ec2.ImageStateEnum.available.value]),
        ],
    ).one()
    image_id = image.id

    # update tags
    create_tags_kwargs = dict(
        Resources=[
            image_id,
        ]
    )
    if tags:
        create_tags_kwargs["Tags"] = [dict(Key=k, Value=v) for k, v in tags.items()]

    # create tags will overwrite the existing tags
    ec2_client.create_tags(**create_tags_kwargs)
    return image_id
