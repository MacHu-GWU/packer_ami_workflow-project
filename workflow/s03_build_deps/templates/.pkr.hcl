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
  instance_type = "t3.large"
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
  name    = "install build dependencies"
  sources = [
    "source.amazon-ebs.ubuntu20"
  ]

  provisioner "shell" {
    inline = [
      # wait until the machine fully boots up
      "sleep 10",
      # note, we don't install MySQL via apt-get, it is already installed in the previous AMI
      "sudo apt-get update -y && sudo apt-get install git cmake make gcc g++ clang libmysqlclient-dev libssl-dev libbz2-dev libreadline-dev libncurses-dev libboost-all-dev -y",
      # libboost-all-dev might have some dependencies issue, we can fix the dependencies and then install
      "sudo apt --fix-broken install -y",
      "sudo apt-get install libboost-all-dev -y",
      "lsb_release -a",
      "openssl version",
      "clang --version",
      "cmake --version",
      "mysql --version",
      "screen --version",
    ]
  }

  provisioner "file" {
    source = "export_build_deps_versions.py"
    destination = "/tmp/export_build_deps_versions.py"
  }

  provisioner "shell" {
    script = "export_build_deps_versions.sh"
  }
}