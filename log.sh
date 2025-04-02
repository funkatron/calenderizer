#!/bin/zsh

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Simple logging function that takes a tag and log level
log() {
    local tag=$1
    local level=$2
    shift 2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Set color based on log level
    local color=$NC
    case "$level" in
        "info") color=$BLUE ;;
        "warning") color=$YELLOW ;;
        "error") color=$RED ;;
        "debug") color=$PURPLE ;;
    esac

    # Console output without tag
    local console_message="$timestamp [$level] $*"
    echo -e "${color}$console_message${NC}"

    # Log file output with tag
    local log_message="$timestamp [$tag] [$level] $*"
    echo "$log_message" >> "${LOG_FILE:-"$(dirname "$0")/app.log"}"
}