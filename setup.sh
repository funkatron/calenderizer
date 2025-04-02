#!/bin/zsh
# setup.sh - Sets up a Python virtual environment, installs dependencies, and runs the iCalendar generator.

# Exit immediately if a command exits with a non-zero status.
set -e

# Source the logging function
source "$(dirname "$0")/log.sh"

# Set the log tag
LOG_TAG="project-calenderizer"

# get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# move to work in the script directory
cd "$SCRIPT_DIR"

# Define the virtual environment directory.
VENV_DIR="$SCRIPT_DIR/venv"

# Check if Python 3 is installed; Homebrew users can install it if missing.
if ! command -v python3.12 &> /dev/null; then
    log "$LOG_TAG" warning "Python3.12 not found. Installing via Homebrew..."
    brew install python@3.12
fi

# Create virtual environment if it doesn't exist.
if [ ! -d "$VENV_DIR" ]; then
    log "$LOG_TAG" debug "Creating virtual environment..."
    python3.12 -m venv "$VENV_DIR"
else
    log "$LOG_TAG" info "Virtual environment already exists"
fi

# Activate the virtual environment.
log "$LOG_TAG" debug "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip.
log "$LOG_TAG" debug "Upgrading pip..."
pip install --upgrade pip

# Create a requirements.txt file with necessary packages.
log "$LOG_TAG" debug "Creating requirements.txt..."
cat <<EOF > "$SCRIPT_DIR/requirements.txt"
icalendar
pytz
EOF

# Install the required dependencies.
log "$LOG_TAG" debug "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Run the Python script to generate the .ics file.
log "$LOG_TAG" debug "Generating calendar file..."
python3 "$SCRIPT_DIR/ics-generator.py"

# Get the full path of the generated file
CALENDAR_FILE="$SCRIPT_DIR/project_schedule.ics"
log "$LOG_TAG" info "Setup complete! Your calendar file is ready at: $CALENDAR_FILE"
log "$LOG_TAG" info "You can now import this file into your calendar application."