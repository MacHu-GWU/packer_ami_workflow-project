Built Core
==============================================================================
This packer script is to clone azerothcore-wotlk git repo and build server core from it. It also build optional modules. After build, it will create a metadata file with the commit id. So you can use the commit id to rebuild anytime.

The source code is around 700 MB built server is around 700MB, but it will leave around 5G temporary build data in the ``build`` folder. It is better to delete the temporary build folder ``azerothcore-wotlk`` after the build is done, you have the commit id and you can clone that historical version any time later.

Build time is around 13 minutes on c5.9xlarge.

Build core is a CPU intensive work, and it can leverage all CPU to build it concurrently.

- t3.2xlarge: 8 vCPU, 32GB RAM
- c5.4xlarge: 16 vCPU, 32GB RAM
- c5.9xlarge: 36 vCPU, 72GB RAM
