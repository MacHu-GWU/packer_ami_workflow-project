.. _install-packer:

Install Packer
==============================================================================
首先我们要安装 hashicorp packer.

:class:`~packer_ami_workflow.packer.PackerInstaller` 可以自动化安装 packer pre-compiled binary. 使用方法可以参考 `install_packer.py <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/debug/install_packer.py>`_. 下面是这个例子的源代码:

.. dropdown:: install_packer.py

    .. literalinclude:: ../../../debug/install_packer.py
       :language: python
       :linenos:
