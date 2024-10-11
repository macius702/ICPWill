#!/bin/bash
# filter_output.sh

# Path to the file containing regular expressions
FILTER_FILE="filter_rules.txt"
LOG_FILE="filter_debug.log"

# Clear the log file at the start
> "$LOG_FILE"

# Check if the filter file exists and is readable
if [ ! -r "$FILTER_FILE" ]; then
    echo "Filter file '$FILTER_FILE' does not exist or is not readable." >> "$LOG_FILE"
    exit 1
else
    echo "Filter file '$FILTER_FILE' found and is readable." >> "$LOG_FILE"
fi

# Read from stdin
while IFS= read -r line; do
    echo "Processing line: $line" >> "$LOG_FILE"
    matched=false
    regex_read=false  # Flag to check if any regex patterns are read
    # Apply each regular expression to the line
    while IFS= read -r regex || [ -n "$regex" ]; do
        regex_read=true
        echo "Checking regex: $regex" >> "$LOG_FILE"
        if [[ $line =~ $regex ]]; then
            echo "Line matches regex: $regex. Excluding line." >> "$LOG_FILE"
            matched=true
            break  # Stop checking after the first match
        else
            echo "Line does not match regex: $regex" >> "$LOG_FILE"
        fi
    done < "$FILTER_FILE"
    if [ "$regex_read" = false ]; then
        echo "No regex patterns were read from '$FILTER_FILE'." >> "$LOG_FILE"
    fi
    if [ "$matched" = false ]; then
        # If the line does NOT match any regex, print it
        echo "Including line: $line" >> "$LOG_FILE"
        echo "$line"
    fi
done
