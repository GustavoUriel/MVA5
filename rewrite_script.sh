#!/bin/bash

# Counter file
COUNTER_FILE="/tmp/git_rewrite_counter"
echo "0" > "$COUNTER_FILE"

# Read commit messages
MESSAGES=($(cat commit_messages.txt))

# Message filter function
msg_filter() {
    local counter=$(cat "$COUNTER_FILE")
    
    if [ $counter -lt ${#MESSAGES[@]} ]; then
        echo "${MESSAGES[$counter]}"
    else
        echo "feat: Additional development improvements"
    fi
    
    echo $((counter + 1)) > "$COUNTER_FILE"
}

# Export the function and run git filter-branch
export -f msg_filter
export COUNTER_FILE
export MESSAGES

# Set author information
export GIT_AUTHOR_NAME="Scientific Research Team"
export GIT_AUTHOR_EMAIL="research@microbiome-analysis.com"
export GIT_COMMITTER_NAME="Scientific Research Team"
export GIT_COMMITTER_EMAIL="research@microbiome-analysis.com"

# Run git filter-branch
git filter-branch \
    --msg-filter 'msg_filter' \
    --env-filter '
        export GIT_AUTHOR_NAME="Scientific Research Team"
        export GIT_AUTHOR_EMAIL="research@microbiome-analysis.com"
        export GIT_COMMITTER_NAME="Scientific Research Team"
        export GIT_COMMITTER_EMAIL="research@microbiome-analysis.com"
    ' \
    -- --all

# Clean up
rm -f "$COUNTER_FILE"
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

echo "Git history rewrite completed!"

