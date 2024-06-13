packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = "~> 1"
    }
  }
}

source "amazon-ebs" "ubuntu20" {
  ami_name      = var.output_ami_name
  instance_type = "t2.micro"
  region        = var.aws_region
  ssh_username  = "ubuntu"

  /*----------------------------------------------------------------------------
  You can either explicitly specify the ``source_ami`` field or use the ``source_ami_filter``
  to find the AMI ID automatically. I personal prefer to provide the ``source_ami``
  explicitly for better control.
  https://developer.hashicorp.com/packer/integrations/hashicorp/amazon/latest/components/builder/ebs
  ----------------------------------------------------------------------------*/
  source_ami = var.source_ami_id

  # if none default VPC, you need to explicitly set this to true
  associate_public_ip_address = true

  # make sure you are using a public subnet
  subnet_filter {
    filters = {
      "tag:Name": var.subnet_name,
    }
    most_free = true
    random = false
  }

  # make sure the security group has ssh inbound rule
  security_group_filter {
    filters = {
      "tag:Name": var.security_group_name,
    }
  }
}

build {
  name    = "install python"
  sources = [
    "source.amazon-ebs.ubuntu20"
  ]

  provisioner "shell" {
    inline = [
      "sleep 10",
    ]
  }


  /*----------------------------------------------------------------------------
  if you need to sudo install something, do it in the ``inline`` block
  ----------------------------------------------------------------------------*/
  provisioner "shell" {
    inline = [
      "echo provision step 2",
    ]
  }
}