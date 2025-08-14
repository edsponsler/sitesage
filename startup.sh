#!/bin/bash
# This script loads environment variables from a .env file
# and prints the key-value pairs that were set.

set -e

if [ -f .env ]; then
  echo "Loading and exporting variables from .env file..."
  # Read each line, ignore comments and empty lines, then export.
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ ! "$line" =~ ^\s*# && "$line" =~ = ]]; then
      export "$line"
      echo "Set: $line"
    fi
  done < .env
  echo "
Environment variables set successfully."
else
  echo "No .env file found."
fi
