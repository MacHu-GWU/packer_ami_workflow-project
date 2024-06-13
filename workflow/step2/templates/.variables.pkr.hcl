variable "source_ami_id" {
  type        = string
  description = "Base AMI ID to use for building this AMI, I prefer to explicitly provide this value."
}

variable "output_ami_name" {
  type        = string
  description = "The generated AMI name, it has to be unique in a region."
}


variable "aws_region" {
  type        = string
  description = "The AWS region where the AMI will be created."
}

variable "vpc_name" {
  type        = string
  description = "The VPC name where the packer build will run."
}

variable "is_default_vpc" {
  type        = string
  description = "are we using default VPC? use false or true (string, not boolean)."
}

variable "subnet_name" {
  type        = string
  description = "The Subnet name where the packer build will run."
}

variable "security_group_name" {
  type        = string
  description = "The Security name where the packer build will use."
}

variable "ec2_iam_role_name" {
  type        = string
  description = "The IAM role name that the packer build will use."
}
