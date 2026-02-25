#!/bin/bash
VENV_DIR="/home/jab/projects/new/keyholder/venv"
source "$VENV_DIR/bin/activate"
python3 "/home/jab/projects/new/keyholder/main.py" "$@"
