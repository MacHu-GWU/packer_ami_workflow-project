This is an example folder structure for a packer build project.

The ``templates`` folder stores the ``*.hcl`` written in `jinja2 template <https://jinja.palletsprojects.com/>`_ formats. The python script `packer_build.py <./packer_build.py>`_ defines the project-width parameters and those parameters are used for rendering the ``*.hcl`` files. For example, the ``*.pkrvars.hcl`` file will be rendered based on the parameters and will be passed to the ``packer build`` command.

Please read the `template/.pkr.hcl <./template/.pkr.hcl>`_ file for more best practice writing a packer script.
