# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from packer_ami_workflow.tests import run_cov_test

    run_cov_test(__file__, "packer_ami_workflow", is_folder=True, preview=False)
