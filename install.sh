#!/bin/bash

# Exit on any error
set -e

# Directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$DIR/venv"
INSTALL_BIN="$HOME/.local/bin"

echo "Setting up Keyholder CLI..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install requirements
echo "Installing requirements..."
pip install -r "$DIR/requirements.txt"

# Create a wrapper script using absolute paths
WRAPPER_SCRIPT="$DIR/keyholder_wrapper.sh"
cat << EOF > "$WRAPPER_SCRIPT"
#!/bin/bash
VENV_DIR="$VENV_DIR"
source "\$VENV_DIR/bin/activate"
python3 "$DIR/main.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Make sure the local bin directory exists
mkdir -p "$INSTALL_BIN"

# Create a symlink to the wrapper
LINK_NAME="keyholder"
if [ -L "$INSTALL_BIN/$LINK_NAME" ]; then
    rm "$INSTALL_BIN/$LINK_NAME"
fi

ln -s "$WRAPPER_SCRIPT" "$INSTALL_BIN/$LINK_NAME"

echo ""
echo "Installation complete!"
echo "The command '$LINK_NAME' is now available in your terminal."
echo "If it says 'command not found', make sure '$INSTALL_BIN' is in your PATH."
echo "You can test it by running: keyholder -h"
