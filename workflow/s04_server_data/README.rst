Server Data
==============================================================================
This packer script is to download server data and unzip it. If we do that with following step together, the change of snapshot would be to large and will too long to create.

The total size of the server data is about 1.2GB (zipped) and 3.3GB (unzipped). So we may use the default EBS volume (8GB) as it is.

Build time is around 10 minutes on t3.large.

Reference:

- Downloads data: https://www.azerothcore.org/wiki/server-setup
