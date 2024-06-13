#!/bin/bash -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pip3.10 install pathlib_mate
python3.10 /tmp/download_server_data.py
