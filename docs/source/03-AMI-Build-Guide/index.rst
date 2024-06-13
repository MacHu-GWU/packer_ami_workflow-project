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
3. 用 jinja2 语言 render 最终的 hcl 文件, 并将其放在 Step 的目录下.

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


Manage AMIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
AWS 官方有很多 AMI API 可以进行 list, get details 等操作. 但是灵活性还是远远不如用数据库来管理 metadata. 所以在这个项目中我们会用 DynamoDB 来管理 AMI 的 metadata, 使得我们可以更方便地操作 AMI.

:class:`~packer_ami_workflow.dynamodb.AmiData` 是一个 ORM 类, 它能让开发者用 Pythonic 的方式操作 DynamoDB, 并封装了常用的 query pattern, 例如:

- :meth:`~packer_ami_workflow.dynamodb.AmiData.get_image`
- :meth:`~packer_ami_workflow.dynamodb.AmiData.query_by_workflow`
- :meth:`~packer_ami_workflow.dynamodb.AmiData.query_by_step_id`


Packer Build Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. important::

    这一步就是我们真正作为一个 AMI 的维护着要动手写的部分了.

这个 `packer_ami_workflow/tests/example.py <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/packer_ami_workflow/tests/example.py>`_ 是一个非常薄的 wrapper, 把 ``packer_ami_workflow`` 库的 utility 扩展, 并封装了一下. 它展示了你如何扩展默认的 :class:`~packer_ami_workflow.param.WorkflowParam` 和 :class:`~packer_ami_workflow.param.StepParam` 类, 如何指定 :class:`~packer_ami_workflow.dynamodb.AmiData` DynamoDB Table 的名字.

.. dropdown:: packer_ami_workflow/tests/example.py

    .. literalinclude:: ../../../packer_ami_workflow/tests/example.py
       :language: python
       :linenos:

有了这个 wrapper 之后, 开发者唯一要做的事情就只有三个:

1. 编写 `/workflow/step1/template <https://github.com/MacHu-GWU/packer_ami_workflow-project/tree/main/workflow/step1/templates>`_ 中的 packer template 的逻辑. 具体语法和细节你可以参考 `packer 的官方文档 <https://developer.hashicorp.com/packer/tutorials/aws-get-started/aws-get-started-build-image>`_.
2. 填写 `/workflow/workflow_param.json <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/workflow_param.json>`_ 和 `/workflow/step1/step_param.json <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1/step_param.json>`_ 配置文件.
3. 运行 `/workflow/step1/packer_build.py <https://github.com/MacHu-GWU/packer_ami_workflow-project/blob/main/workflow/step1/packer_build.py>`_ 脚本.

**下面我们来详细讲一讲** ``packer_build.py`` **脚本的结构**. 首先, 我们来看一下这个脚本的源码.

.. important::

    ``packer_build.py`` 也是我们的核心脚本之一, 我建议仔细阅读 ``packer_build.py`` 源码中的注释来了解这个脚本的逻辑.

.. dropdown:: packer_build.py

    .. literalinclude:: ../../../packer_workspaces/example/packer_build.py
       :language: python
       :linenos:

这个脚本的内容很简单:

1. 创建一个 AmiBuilder 对象, 这个对象在前面提到的 ``packer_ami_workflow/tests/example.py`` wrapper 中已经写好了.

.. code-block:: python

    builder = AmiBuilder.make_builder(dir_step=dir_here)

2. 用 packer build 命令创建 AMI.

.. code-block:: python

    # dry_run is True = NOTHING happen, False = run packer build
    builder.run_packer_build_workflow(dry_run=True)

3. 给 AMI 打 AWS Tags.

.. code-block:: python

    builder.tag_ami()

4. 在 DynamoDB 中创建一条记录.

.. code-block:: python

    builder.create_dynamodb_item()

5. (Optional) 删除 AMI, 并可以选择是否同时删除 snapshot.

.. code-block:: python

    builder.delete_ami(delete_snapshot=False, skip_prompt=False)

还有一种特殊情况是, 这个 packer template 中有一些步骤真的无法通过自动化完成, 那么你可以手动用前一步的 AMI 创建 EC2, 然后 SSH 进去, 手动 provision 环境, 退出然后 stop instance, 手动 create image, 然后 terminate instance. (我这里有个小工具可以方便的 SSH 到 EC2
`ssh2awsec2 <https://github.com/MacHu-GWU/ssh2awsec2-project>`_). 下面是一个例子:

.. code-block:: python

    # 手动填写这个 ec2 instance id
    builder.create_image_manually(instance_id="i-a1b2c3d4")
