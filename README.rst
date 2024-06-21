
.. image:: https://readthedocs.org/projects/packer-ami-workflow/badge/?version=latest
    :target: https://packer-ami-workflow.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/packer_ami_workflow-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/packer_ami_workflow-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/packer_ami_workflow-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/packer_ami_workflow-project

.. image:: https://img.shields.io/pypi/v/packer-ami-workflow.svg
    :target: https://pypi.python.org/pypi/packer-ami-workflow

.. image:: https://img.shields.io/pypi/l/packer-ami-workflow.svg
    :target: https://pypi.python.org/pypi/packer-ami-workflow

.. image:: https://img.shields.io/pypi/pyversions/packer-ami-workflow.svg
    :target: https://pypi.python.org/pypi/packer-ami-workflow

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/packer_ami_workflow-project

------

.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://packer-ami-workflow.readthedocs.io/en/latest/

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://packer-ami-workflow.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/packer_ami_workflow-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/packer_ami_workflow-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/packer_ami_workflow-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/packer-ami-workflow#files


Welcome to ``packer_ami_workflow`` Documentation
==============================================================================
.. image:: https://packer-ami-workflow.readthedocs.io/en/latest/_static/packer_ami_workflow-logo.png
    :target: https://packer-ami-workflow.readthedocs.io/en/latest/

我在生产实践中使用 packer 来构建 `Amazon Machine Image <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html>`_ 总结了一套最佳实践, 用于维护 AMI 数量非常多, Provision 逻辑非常复杂的项目. 其核心思想是将一个复杂的 provision 过程分拆成多个 step, 然后这些 step 按照顺序组合成一个 workflow, 运维人员可以每隔一段时间就重新运行一次这个 workflow 以更新镜像.

为了方便开发人员能快速上手这套最佳实践, 我设计了一套目录结构以及框架, 使得即时没有经验的开发者都可以用类似填表那样的傻瓜式操作管理复杂项目.


.. _install:

Install
------------------------------------------------------------------------------

``packer_ami_workflow`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install packer-ami-workflow

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade packer-ami-workflow
