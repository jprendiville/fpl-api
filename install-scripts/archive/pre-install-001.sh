# install-scripts/pre-install-001.sh
#!/bin/sh

echo "Running pre-install script 001..."

psql -h db -U fpl -d python_fpl -c "update common_lastupdated set fpl_data = null;"

echo "Pre-install script 001 completed."
