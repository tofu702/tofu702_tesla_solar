#!/bin/bash
# Find the full path to this script
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
ENV_PATH="$SCRIPT_DIR/env"
ENV_PIP="$ENV_PATH/bin/pip"


devbox run python -m venv $ENV_PATH
$ENV_PIP install -r ./requirements.txt
