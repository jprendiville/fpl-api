#!/bin/sh
set -e

# Check if the parameter is provided
if [ -z "$1" ]; then
    echo "Usage: $0 {pre|post}"
    exit 1
fi

# Directory for install scripts
INSTALL_DIR="./install-scripts"
ARCHIVE_DIR="$INSTALL_DIR/archive"

# Create archive directory if it doesn't exist
mkdir -p "$ARCHIVE_DIR"

# Parameter to determine which scripts to run
PHASE=$1
SCRIPT_PREFIX="${PHASE}-install"

echo "Running ${PHASE}-install scripts..."

# Loop through each script with the specified prefix
for script in "$INSTALL_DIR"/${SCRIPT_PREFIX}*; do
    if [ -f "$script" ]; then
        echo "Executing $script..."
        chmod +x "$script"
        ./"$script"

        # Move script to archive after successful execution
        mv "$script" "$ARCHIVE_DIR"
        echo "Archived $script"
    fi
done

echo "${PHASE}-install scripts completed."
