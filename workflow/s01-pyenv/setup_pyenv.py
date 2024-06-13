#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This shell script adds necessary initialization code to ~/.bashrc file for pyenv.
"""

from pathlib import Path

dir_home = Path.home()
path_bashrc = dir_home / ".bashrc"

# add lines to ~/.bashrc file
with path_bashrc.open("a") as f:
    f.write("\n")
    for line in [
        'export PYENV_ROOT="$HOME/.pyenv"',
        'export PATH="$PYENV_ROOT/bin:$PATH"',
        'eval "$(pyenv init -)"',
    ]:
        f.write(f"{line}\n")
