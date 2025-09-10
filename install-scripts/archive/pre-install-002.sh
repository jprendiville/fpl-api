# install-scripts/pre-install-002.sh
#!/bin/sh

echo "Running pre-install script 002 to drop players_team/players_teampreviousposition for #208/#218..."

psql -h db -U fpl -d python_fpl -c "DROP TABLE players_team CASCADE;"
psql -h db -U fpl -d python_fpl -c "DROP TABLE players_teampreviousposition CASCADE;"

echo "Pre-install script 002 completed."
