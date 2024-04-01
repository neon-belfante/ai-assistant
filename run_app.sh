#!/bin/bash

# Determine the directory of the bash script
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Define the path to the virtual environment directory
venv_dir="${script_dir}/ai-environment"

# Activate the virtual environment
source "${venv_dir}/bin/activate"

# Run the Python application
python3 "${script_dir}/gtk_gui.py"

# Deactivate the virtual environment upon termination
deactivate