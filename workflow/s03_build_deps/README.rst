Build Dependencies
==============================================================================
This packer script is to install necessary build dependencies for building the core. NOTE, MySQL is already built in the previous step.

Requirements, as of 2023-03-20:

- Ubuntu >= 20.04 LTS (Focal Fossa)
- MySQL ≥ 5.7.0 (8.x.y is recommended)
- Boost ≥ 1.74
- OpenSSL ≥ 1.0.x
- CMake ≥ 3.16
- Clang ≥ 10

If you use the ubuntu 18, then the max version of a lot of tools are too old, and you cannot update them via ``apt-get``, you have to install them manually, which is too complicated. So I would like to use ubuntu 20 as the base image.

Check the versions::

    # check ubuntu version
    $ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 20.04.5 LTS
    Release:        20.04
    Codename:       focal

    # check openssl version
    openssl version
    OpenSSL 1.1.1f  31 Mar 2020

    # check clang version
    clang --version

    # check cmake version
    cmake --version

    # check mysql version
    mysql --version

The total size of the installed dependencies is about 1GB. So we may use the default EBS volume (8GB) as it is.

Build time is around 10 minutes on t3.large.

Reference:

- Linux Requirements: https://www.azerothcore.org/wiki/linux-requirements
