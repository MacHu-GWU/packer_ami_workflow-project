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
  instance_type = "c5.9xlarge"
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

  launch_block_device_mappings {
      device_name = "/dev/sda1"
      delete_on_termination = true
      volume_type = "gp3"
      volume_size = 20
  }

  ami_block_device_mappings {
     device_name = "/dev/sda1"
     delete_on_termination = true
     volume_type = "gp3"
  }
}

build {
  name    = "build azeroth core"
  sources = [
    "source.amazon-ebs.ubuntu20"
  ]

  provisioner "shell" {
    inline = [
      # wait until the machine fully boots up
      "sleep 10",
      # verify ebs attachment
      "lsblk",
      "df -h",
    ]
  }

  provisioner "file" {
    source = "build_core.py"
    destination = "/tmp/build_core.py"
  }

  provisioner "shell" {
    script = "build_core.sh"
  }

  provisioner "shell" {
    inline = [
      # verify
      "ls ~/azeroth-server",
      "ls ~/azeroth-server/bin",
      "ls ~/azeroth-server/etc",
    ]
  }
}