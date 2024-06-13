MySQL
==============================================================================


Overview
------------------------------------------------------------------------------
这一步骤的目的是从源码安装某个具体版本的 MySQL, 而且这一个步骤只能手动进行, 无法使用 packer 自动化. 这里我们解释一下原因.

**为什么要安装特定的版本?**

    因为你在 build 服务器核心的时候, 编译的过程中就会读取在 build 环境中已经安装好的 MySQL 的版本, 并且在核心里也会写入这个版本. 然后核心用 MySQL 连接数据库的时候会跟数据库中的版本进行比对, 如果不一致则你无法启动服务器. 这就意味着你的 MySQL client, 服务器核心, 数据库中的 MySQL 版本都必须是一致的.

**为什么要从源码安装?**

    因为 apt-get 的命令无法指定安装特定版本. 从源码安装能让你更清楚的知道你到底安装了什么版本.

**为什么无法使用 Packer 自动化?**

    从源码安装的步骤里有几个命令是在 terminal 中弹出一个虚拟窗口然后用方向键选择跟窗口互动. 这部分 packer 是无法自动化的, 所以只能手动.

**关闭 AWS RDS 的自动升级 patch 版本的选项.**

    前面说了, MySQL client, 服务器核心, 数据库中的 MySQL 版本都必须是一致的, 没有必要频繁的升级数据库版本. 这个选项是默认打开的, 你如果不关闭, 那么一旦你的数据进行了自动升级, 你的服务器就无法启动了.

**如何升级数据库?**

    这通常是因为你使用了 `Upgrade MySQL DB engine <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.MySQL.html>`_ 功能升级了数据库, 然后你需要重新安装 MySQL client 以及 build 你的服务器核心. 你需要回到 MySQL 这一步骤, 重新 build AMI. 然后在这个 AMI 的基础上重新 build 核心. 升级数据库的时候一定要注意先用 Snapshot 做一个备份, 然后从备份恢复一个新的数据库, 然后在新的数据库上进行测试. 然后用 Blue / Green 的模式部署, 确保现有的服务器和数据库没有问题.


Runbook
------------------------------------------------------------------------------
总的来说有以下五个步骤, 其中 #2 需要运行几个命令.

1. start instance from AMI
2. install MySQL and cleanup
3. stop instance
4. create AMI
5. terminate instance

下面的命令是你 SSH 到 EC2 上, 安装 MySQL 的详细命令.

.. code-block:: bash

    # 创建一个新目录
    mkdir ~/install-mysql

    # 进入这个目录
    cd ~/install-mysql

    # 该链接可以在 https://downloads.mysql.com/archives/community/ 找到
    wget https://downloads.mysql.com/archives/get/p/23/file/mysql-server_8.0.28-1ubuntu20.04_amd64.deb-bundle.tar

    # 解压安装包
    tar -xvf mysql-server_8.0.28-1ubuntu20.04_amd64.deb-bundle.tar

    # 安装构建依赖
    sudo apt-get install -y libaio1

    # 对 mysql server 进行预配置
    # 它会在 terminal 里弹出一个窗口, 你要用方向键选择选项然后按回车
    # 这里会要求你创建 root password, 你可以随便输入一个, 因为最终我们的 MySQL 是在 RDS 上
    # 而不是本地. 我填的是 NYz&xrM5biYA, 被人看到也无所谓.
    sudo dpkg-preconfigure mysql-community-server_*.deb

    # 安装 mysql server
    # 这里通常会弹出一个警告, 说你缺少 libmecab2 依赖,
    # 然后你可以运行 sudo apt-get -f install 来强制安装 (官方说的)
    sudo dpkg -i mysql-{common,community-client-plugins,community-client-core,community-client,client,community-server-core,community-server,server}_*.deb

    # 至此 MySQL 的安装已经完成.

安装完毕后, 你可以进行 #3, stop instances, 然后等待 instance 停止. 然后进行 #4. create AMI 这一步骤我们有一个自动化脚本 ``create_image.py``.

创建完 image 之后就可以 terminate EC2 了.

**Reference**:

- Linux Requirements: https://www.azerothcore.org/wiki/linux-requirements
- `MySQL Product Archives <https://downloads.mysql.com/archives/community/>`_: MySQL 所有历史版本, 不同 OS, 不同平台的下载链接. 这里我们要选择 MySQL 版本, OS 为 Ubuntu Linux, OS Version 为 20.04. 然后 DEB Bundle 是下面所有组件的打包, 下载这一个就够了.
- `Installing MySQL on Linux Using Debian Packages from Oracle <https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/linux-installation-debian.html>`_: 这篇是 MySQL 官方文档, 讲述了如何从 debian 的 distribution 包 (源码包) 中为 ubuntu 安装具体版本的 MySQL.
