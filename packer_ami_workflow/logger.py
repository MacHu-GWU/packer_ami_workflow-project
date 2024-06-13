# -*- coding: utf-8 -*-

from .vendor.nested_logger import NestedLogger

logger = NestedLogger(
    name="packer4ami",
    log_format="%(message)s",
)
