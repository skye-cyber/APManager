#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root${NC}"
    exit 1
fi

# Define the rules to add
RULES=(
    'ALL ALL=NOPASSWD: /home/skye/.local/bin/ap_manager'
    'ALL ALL=NOPASSWD: /home/skye/.local/bin/ap, /etc/ap_manager/proc/'
)

# Check if rules already exist
for rule in "${RULES[@]}"; do
    if sudo grep -q "$rule" /etc/sudoers; then
        echo -e "${YELLOW}Rule already exists: $rule${NC}"
        continue
    fi

    # Add the rule
    echo -e "${YELLOW}Adding rule: $rule${NC}"
    echo "$rule" | sudo EDITOR='tee -a' visudo
done

echo -e "${GREEN}Sudoers configuration updated successfully${NC}"
