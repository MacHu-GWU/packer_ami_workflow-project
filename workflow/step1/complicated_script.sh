#!/bin/bash
#
# This is an example script to run arbitrary complicated provisioning logics
# in Python. Basically, you can put your provisioning logics in a Python library
# (not just a script, but a library that split logics into modules and import
# each other). Then you can use this script to:
#
# 1. clone the repo from git
# 2. create Python virtualenv and install dependencies
# 3. run your provisioning script

# clone the git repo that contains your automation scripts
git clone https://github.com/MacHu-GWU/packer_ami_workflow-project

# the current dir will be changed for all the following commands
cd packer_ami_workflow-project || exit

# create the virtualenv and install dependencies via poetry
sudo python3 install --disable-pip-version-check virtualenv
virtualenv -p python3 .venv
./.venv/bin/pip install -r requirements.txt

# now you can use your virtualenv to run any complicated script
./.venv/bin/python ./packer_workspaces/example/complicated_script.py
