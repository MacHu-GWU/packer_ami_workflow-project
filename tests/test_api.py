# -*- coding: utf-8 -*-

from packer_ami_workflow import api


def test():
    _ = api


if __name__ == "__main__":
    from packer_ami_workflow.tests import run_cov_test

    run_cov_test(__file__, "packer_ami_workflow.api", preview=False)
