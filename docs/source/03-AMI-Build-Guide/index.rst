AMI Build Guide
==============================================================================
本章详细介绍了作为一个开发者, 应该如何使用这个库来管理复杂的 packer build AMI 项目.


The ``workflow`` Folder
------------------------------------------------------------------------------
**Folder Structure**

在这个 Repo 的根目录下有一个 `workflow <https://github.com/MacHu-GWU/packer_ami_workflow-project/tree/main/workflow>`_ 目录. 里面包含一个 ``workflow_param.json`` 和一堆文件夹. 里面的目录结构大致长下面这样.

.. code-block::

    /workflow/
    /workflow/{step1_workspace}/
    /workflow/{step2_workspace}/
    /workflow/.../
    /workflow/find_root_base_image_id.py
    /workflow/workflow_param.json

如果你还记得 :ref:`workflow-and-step-strategy` 中提到的我们将一个 AMI 的多个步骤拆分的策略, 整个 ``workflow`` 就是一个 workflow. 而这里的每个子目录就是一个 Step.

**Step1**

而 `step1 <https://github.com/MacHu-GWU/packer_ami_workflow-project/tree/main/workflow/step1>`_ 是一个特殊的 Step. 它是这个 workflow 中的第一个 step, 同时它给出了一个典型的 step 的目录下的代码结构. 所有真正要用的 step 都是用这个 step1 作为模板来创建的.

**Find root base image id script**

通常一个 workflow 起始于一个 base image, 它被称为整个 workflow 中所有 step 的 root base image. `find_root_base_image_id.py <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/find_root_base_image_id.py>`_ 是一个脚本筛选 base image 的. 在这个例子中, 我们筛选出指定 ubuntu 发行版中的最新版本作为 root base image. 获得了 image id 和 image name 之后我们就可以将其填入 ``workflow_param.json`` 文件中 (详情请看下一节).

.. dropdown:: find_root_base_image_id.py

    .. literalinclude:: ../../../workflow/find_root_base_image_id.py
       :language: javascript
       :linenos:

**Workflow Parameter JSON File**

这些 Step 的 packer template 中都会有很多 parameter, 而这里很多 Step 的 parameter 都是一样的. 而 `/workflow/workflow_param.json <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/workflow_param.json>`_ 就保存了这些通用的 parameter 的值.

.. dropdown:: workflow_param.json

    .. literalinclude:: ../../../workflow/workflow_param.json
       :language: javascript
       :linenos:


.. _per-step-folder:

Per Step Folder
------------------------------------------------------------------------------
下面我们进到一个 `具体的 Step1 目录里 <https://github.com/MacHu-GWU/packer_ami_workflow-project/tree/main/workflow/step1>`_ 看看每个 Step 的 packer template 应该怎么写. 下面列出了 Step 的 workspace 的目录结构.

.. code-block::

    # 核心文件
    /workspace/
    /workspace/templates/
    /workspace/templates/.pkr.hcl
    /workspace/templates/.pkrvars.hcl
    /workspace/templates/.variables.pkr.hcl
    /workspace/.gitignore
    /workspace/packer_build.py # <--- 用这个脚本运行 packer build
    /workspace/param.json

    # 这个例子展示了在无需任何 python 库的情况下, 使用 python shell script 来实现 provision 逻辑
    /workspace/zero_deps_script.py
    # 这个例子展示了在需要少量 python 库的情况下, 使用 python shell script 来实现 provision 逻辑
    /workspace/some_deps_script.py
    # 这个例子展示了如何实现非常复杂的 provision 逻辑
    # 其核心就是用 .sh 来给 Python 安装依赖
    # 然后用 .py 来实现复杂的 provision 逻辑
    /workspace/complicated_script.py
    /workspace/complicated_script.sh
    /workspace/README.rst

在详细展开之前, 我们先来了解一下 ``/workspace/templates/`` 目录:


.. _prepare-packer-templates:

Prepare Packer Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`Packer 原生的 Template <https://developer.hashicorp.com/packer/docs/templates/hcl_templates>`_ 本质上相当于一个 declaration (声明式) 的脚本. 这有点类似于 CloudFormation, 它不是面像过程, 而是声明式的. 但是它有着声明式脚本的通用缺点, 自动化程度不高, 参数化系统不够灵活, 你无法基于 parameter 来用 if else, for loop 等对整个 template 的结构进行控制. 所以我在 Template 上又用 `jinja2 <https://jinja.palletsprojects.com/en/3.1.x/>`_ 模板引擎封装了一层 (这跟我初期改进 CloudFormation 流程的做法类似). 具体来说整个开发流程是这样的:

1. 用 jinja2 语言写 hcl 模板. 其中使用一个 ``params`` Python 对象作为所有的 parameter 的 container, 然后用 ``{{ params.parameter_name }}`` 这样的语法来插入参数. 所有的 jinja2 模板都放在 templates 目录下.
2. 在 Python 脚本中生成 params 对象, 至于 params 的数据放在哪里由开发者自己决定. 一般是放在 JSON 里.
3. 用 jinja2 语言 render 最终的 hcl 文件, 并将其放在对应的目录下.

其中在 #1 这一步, 我们有三个关键文件:

- `.pkr.hcl <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1/templates/.pkr.hcl>`_: packer template 的主脚本, 定义了 packer build 的逻辑.
- `.variables.pkr.hcl <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1/templates/.variables.pkr.hcl>`_: packer variables 的声明文件. 注意这里只是定义, 而不包含 value. (see `Input Variables and local variables <https://developer.hashicorp.com/packer/guides/hcl/variables>`_ for more information)
- `.pkrvars.hcl <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1/templates/.pkrvars.hcl>`_: packer variables 的值. packer build 的时候会从这里面读数据.

在编写 ``*.pkr.hcl`` 的时候, 所有在 packer template 中以 string replacement 存在的参数 (例如 ``ami_name      = var.output_ami_name``) 都需要在 ``*.variables.pkr.hcl`` 中定义. 这样能充分利用 packer 的 declaration 语法记录每个 variable 是用来干什么的. 请不要用 ``{{ param.output_ami_name }}`` 这样的语法直接替换掉里面的值, 这样做会降低代码的可维护性. 而如果是用来控制 template 结构的参数我们就不要放在 ``*.variables.pkr.hcl`` 中了. 我认为不应该用 jinja2 template 来完全替代 packer 的 variables 系统, 因为 jinja2 主要是一个 string template engine, 插入值的时候并不会检查类型, 所以我们只用 jinja2 来做 string manipulation, if/else, for loop.

下面我们给出了在 `step1 <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1>`_ 中的这三个关键文件的源代码:

.. important::

    ``.pkr.hcl`` 最为重要, 请仔细阅读其中的注释. 特别是里面关与如何用复杂的 Python 自动化脚本来执行 provision 的相关介绍.

.. dropdown:: .pkr.hcl

    .. literalinclude:: ../../../workflow/step1/templates/.pkr.hcl
       :language: hcl
       :linenos:

.. dropdown:: .pkrvars.hcl

    .. literalinclude:: ../../../workflow/step1/templates/.pkrvars.hcl
       :language: hcl
       :linenos:

.. dropdown:: .variables.pkr.hcl

    .. literalinclude:: ../../../workflow/step1/templates/.variables.pkr.hcl
       :language: hcl
       :linenos:


Step Level Parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
和前面 ``workflow_param.json`` 类似, `step_param.json <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1/step_param.json>`_ 保存了跟这个 step 相关的一些参数. 其中最关键的就是这一步的 step id 和前一步的 step id. 如果当前 step 就是第一步, 那么 ``previous_step_id`` 就是 ``None``.

.. dropdown:: step_param.json

    .. literalinclude:: ../../../workflow/step1/step_param.json
       :language: javascript
       :linenos:


Packer Build Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
每个 Step 目录下都会有一个 ``packer_build.py`` 脚本用于执行 AMI 构建. 它的逻辑包含这么几个步骤:

1. 读取 parameter, 包括 :class:`~acore_ami.workspace.WorkflowParam` 和 :class:`~acore_ami.workspace.StepParam` 两部分.
2. 准备好跟 AWS boto session 相关的变量.
3. 生成 ``packer build`` 命令的所需的 asset, 也就是用 jinja2 生成最终的 ``*.pkr.hcl`` 和 variables 文件.
4. 运行 ``packer build`` 命令, 生成 AMI. 其中 #3, #4 的逻辑被打包在了 :meth:`acore_ami.workspace.Workspace.run_packer_build_workflow` 方法中.
5. 对生成的 AMI 进行管理.给 AMI 打上 Tag, 并在 AMI inventory DynamoDB Table 中创建一条记录.

``packer_build.py`` 这是一个 Python 脚本, 用来运行 packer build. **也是我们的核心脚本**. 这个脚本的主要流程是:

1. 读取 :class:`~acore_ami.workspace.WorkflowParam`
2. 读取 :class:`~acore_ami.workspace.StepParam`
3. 执行 packer build, 包括用 jinja2 render 最终的 packer template, 运行 ``packer validate`` 以及最终运行 ``packer build``, 这些逻辑被 :meth:`acore_ami.workspace.Workspace.run_packer_build_workflow` 方法封装在一起了.
4. 给 AMI 打上 aws tags, 便于管理.
5. 在 DynamoDB 中创建一条记录, 用来记录这个 AMI 的 metadata, 也方便以后进行查询和管理.

.. important::

    ``packer_build.py`` 也是我们的核心脚本之一, 我建议仔细阅读 ``packer_build.py`` 源码中的注释来了解这个脚本的逻辑.

.. dropdown:: packer_build.py

    .. literalinclude:: ../../../packer_workspaces/example/packer_build.py
       :language: python
       :linenos:


Manage AMIs
------------------------------------------------------------------------------
AWS 官方有很多 AMI API 可以进行 list, get details 等操作. 但是灵活性还是远远不如用数据库来管理 metadata. 所以在这个项目中我们会用 DynamoDB 来管理 AMI 的 metadata, 使得我们可以更方便地操作 AMI.
