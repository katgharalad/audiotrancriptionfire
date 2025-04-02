#!/bin/bash
echo "Starting AudioTranscripY + ML Integration..."

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the integration script
python "$DIR/integration/run_integration.py"
