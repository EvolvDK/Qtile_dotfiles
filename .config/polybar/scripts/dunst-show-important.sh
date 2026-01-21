#!/bin/bash

# dunst-show-important.sh
# Script to display important notifications from dunst history based on priority
#
# Priority logic:
# 1. Latest notification with CRITICAL urgency
# 2. If none, latest notification from important applications  
# 3. As fallback, the very latest notification from history

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed." >&2
    exit 1
fi

if ! command -v dunstctl &> /dev/null; then
    echo "Error: dunstctl is not available." >&2
    exit 1
fi

# Exit if dunst is paused
if dunstctl is-paused | grep -q "true" 2>/dev/null; then
    exit 0
fi

# Get notification history
history=$(dunstctl history 2>/dev/null)

# Exit if history is empty or invalid
if [ -z "$history" ] || [ -z "$(echo "$history" | jq -e '.data | flatten | .[0]' 2>/dev/null)" ]; then
    exit 0
fi

# Priority 1: Latest CRITICAL notification
target_id=$(echo "$history" | jq -r '
    .data | flatten | 
    map(select(.urgency.data == "CRITICAL" or .urgency.data == "critical" or .urgency.data == 2)) | 
    if length > 0 then .[-1].id.data else empty end
' 2>/dev/null)

# Priority 2: Latest notification from important applications
if [ -z "$target_id" ]; then
    # Combined regex for better performance - exact match for app names
    important_apps_regex="^(discord|brave|firefox|thunderbird|telegram|slack|teams|element|matrix)$"
    target_id=$(echo "$history" | jq -r --arg regex "$important_apps_regex" '
        .data | flatten | 
        map(select(.appname.data | test($regex; "i"))) | 
        if length > 0 then .[-1].id.data else empty end
    ' 2>/dev/null)
fi

# Priority 3: Latest notification (fallback)
if [ -z "$target_id" ]; then
    target_id=$(echo "$history" | jq -r '
        .data | flatten | 
        if length > 0 then .[-1].id.data else empty end
    ' 2>/dev/null)
fi

# Display notification if found
if [ -n "$target_id" ]; then
    dunstctl history-pop "$target_id" 2>/dev/null
fi
