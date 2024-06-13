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
  # see all ec2 types at: https://aws.amazon.com/ec2/instance-types/
  instance_type = "t3.2xlarge"
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
      # wait until the machine fully boots up
      "sleep 10",
      # install pyenv
      "curl -s https://pyenv.run | bash",
      # verify installation
      "export PYENV_ROOT=\"$HOME/.pyenv\"",
      "export PATH=\"$PYENV_ROOT/bin:$PATH\"",
      "eval \"$(pyenv init -)\"",
      "pyenv --version",
    ]
  }

  provisioner "shell" {
    # set the .bashrc file to enable pyenv in shell
    script = "setup_pyenv.py"
  }

  provisioner "shell" {
    inline = [
      # install developer tools
      "sudo apt-get update -y",
      "sudo apt-get install -y curl",
      "sudo apt-get install -y wget",
      "sudo apt-get install -y git",
      "sudo apt-get install -y unzip",

      # verify
      "which curl",
      "which wget",
      "which git",
      "which unzip",
      "which screen",

      # install necessary dependencies for "pyenv install x.y.z" command
      "sudo apt-get install -y gcc",
      "sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev",
    ]
  }

  provisioner "shell" {
    # install python versions
    # set the global python versions
    script = "install_python_versions.sh"
  }
}