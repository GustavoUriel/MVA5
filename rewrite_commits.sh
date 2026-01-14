#!/bin/bash

# Git History Rewrite Script for Microbiome Analysis Platform
# This script will rewrite all commit messages and author information

set -e  # Exit on any error

echo "🔧 Microbiome Analysis Platform - Git History Rewrite"
echo "=================================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository!"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Get total commit count
COMMIT_COUNT=$(git rev-list --count HEAD)
echo "📊 Total commits to rewrite: $COMMIT_COUNT"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes!"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create backup branch
BACKUP_BRANCH="backup-before-rewrite-$(date +%s)"
echo "💾 Creating backup branch: $BACKUP_BRANCH"
git branch "$BACKUP_BRANCH"

# New author information
export GIT_AUTHOR_NAME="Scientific Research Team"
export GIT_AUTHOR_EMAIL="research@microbiome-analysis.com"
export GIT_COMMITTER_NAME="Scientific Research Team"
export GIT_COMMITTER_EMAIL="research@microbiome-analysis.com"

echo "👤 New author: $GIT_AUTHOR_NAME <$GIT_AUTHOR_EMAIL>"

# Professional commit messages array
declare -a COMMIT_MESSAGES=(
    "feat: Initialize Microbiome Analysis Platform v1.0.0 with Flask architecture"
    "feat: Implement Google OAuth authentication and user management system"
    "feat: Add dataset deletion functionality with confirmation dialogs"
    "feat: Implement file upload validation and data formatting"
    "feat: Add file deletion and management operations"
    "feat: Enhance dashboard UI with animated cards and statistics"
    "feat: Add file editing capabilities with modification tracking"
    "refactor: Remove auxiliary and temporary files from codebase"
    "feat: Implement table viewing and editing module with column preservation"
    "fix: Resolve filter conflicts in table edit due to style insertions"
    "feat: Remove CSV paste functionality and add file renaming"
    "feat: Enhance upload controls with multi-file support and result feedback"
    "feat: Implement file copying functionality"
    "feat: Organize files by type with count displays"
    "feat: Add data curation buttons and status tracking"
    "refactor: Begin major codebase restructuring for better maintainability"
    "refactor: Complete file operations module restructuring"
    "refactor: Complete file editing module restructuring"
    "feat: Preserve column order and save schema in non-edit mode"
    "feat: Implement advanced column preservation with filtered row management"
    "feat: Complete file management module with bug fixes"
    "feat: Create analysis interface with data sources, parameters, and reports tabs"
    "feat: Implement initial analysis page with basic functionality"
    "refactor: Split pages into modules for improved maintainability"
    "refactor: Complete page modularization and separation"
    "feat: Add stratification functionality with mock data"
    "feat: Implement cluster representative selection feature"
    "feat: Add edges selector for network analysis"
    "feat: Populate analysis type configurations"
    "feat: Implement preliminary analysis saving functionality"
    "feat: Add analysis management (ABM) operations"
    "feat: Implement new analysis creation workflow"
    "fix: Implement dataset completion percentage and real-time progress updates"
    "feat: Add comprehensive analysis listing and management interface"
)

echo
echo "⚠️  WARNING: This will rewrite the entire git history!"
echo "⚠️  This action cannot be easily undone!"
echo "⚠️  Make sure you have backups and no one else is working on this repository!"
echo

read -p "Proceed with git history rewrite? (yes/NO): " -r
if [[ ! $REPLY == "yes" ]]; then
    echo "Aborted."
    git branch -D "$BACKUP_BRANCH" 2>/dev/null || true
    exit 0
fi

echo
echo "🚀 Starting git history rewrite..."
echo "This may take a few minutes depending on repository size..."

# Counter for tracking commit index
COMMIT_INDEX=0

# Create a temporary script for the message filter
cat > /tmp/commit_message_filter.sh << 'EOF'
#!/bin/bash

# Array of new commit messages
declare -a MESSAGES=(
    "feat: Initialize Microbiome Analysis Platform v1.0.0 with Flask architecture"
    "feat: Implement Google OAuth authentication and user management system"
    "feat: Add dataset deletion functionality with confirmation dialogs"
    "feat: Implement file upload validation and data formatting"
    "feat: Add file deletion and management operations"
    "feat: Enhance dashboard UI with animated cards and statistics"
    "feat: Add file editing capabilities with modification tracking"
    "refactor: Remove auxiliary and temporary files from codebase"
    "feat: Implement table viewing and editing module with column preservation"
    "fix: Resolve filter conflicts in table edit due to style insertions"
    "feat: Remove CSV paste functionality and add file renaming"
    "feat: Enhance upload controls with multi-file support and result feedback"
    "feat: Implement file copying functionality"
    "feat: Organize files by type with count displays"
    "feat: Add data curation buttons and status tracking"
    "refactor: Begin major codebase restructuring for better maintainability"
    "refactor: Complete file operations module restructuring"
    "refactor: Complete file editing module restructuring"
    "feat: Preserve column order and save schema in non-edit mode"
    "feat: Implement advanced column preservation with filtered row management"
    "feat: Complete file management module with bug fixes"
    "feat: Create analysis interface with data sources, parameters, and reports tabs"
    "feat: Implement initial analysis page with basic functionality"
    "refactor: Split pages into modules for improved maintainability"
    "refactor: Complete page modularization and separation"
    "feat: Add stratification functionality with mock data"
    "feat: Implement cluster representative selection feature"
    "feat: Add edges selector for network analysis"
    "feat: Populate analysis type configurations"
    "feat: Implement preliminary analysis saving functionality"
    "feat: Add analysis management (ABM) operations"
    "feat: Implement new analysis creation workflow"
    "fix: Implement dataset completion percentage and real-time progress updates"
    "feat: Add comprehensive analysis listing and management interface"
)

# Read the counter from file or initialize
if [ -f /tmp/commit_counter ]; then
    COUNTER=$(cat /tmp/commit_counter)
else
    COUNTER=0
fi

# Get the message for current commit
if [ $COUNTER -lt ${#MESSAGES[@]} ]; then
    MESSAGE="${MESSAGES[$COUNTER]}"
else
    MESSAGE="feat: Additional development improvements"
fi

# Increment counter
echo $((COUNTER + 1)) > /tmp/commit_counter

# Output the new message
echo "$MESSAGE"
EOF

chmod +x /tmp/commit_message_filter.sh

# Reset counter
echo "0" > /tmp/commit_counter

# Use git filter-branch to rewrite the history
echo "📝 Rewriting commit messages and author information..."
git filter-branch \
    --msg-filter '/tmp/commit_message_filter.sh' \
    --env-filter '
        export GIT_AUTHOR_NAME="Scientific Research Team"
        export GIT_AUTHOR_EMAIL="research@microbiome-analysis.com"
        export GIT_COMMITTER_NAME="Scientific Research Team"
        export GIT_COMMITTER_EMAIL="research@microbiome-analysis.com"
    ' \
    -- --all

# Clean up temporary files
rm -f /tmp/commit_message_filter.sh /tmp/commit_counter

# Clean up filter-branch backup
echo "🧹 Cleaning up filter-branch backup refs..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

echo
echo "✅ Git history rewrite completed successfully!"
echo

# Show the new history
echo "📋 New commit history:"
echo "----------------------"
git log --oneline --reverse | nl -v0

echo
echo "💾 Backup branch created: $BACKUP_BRANCH"
echo "🔍 To view old history: git log --oneline $BACKUP_BRANCH"
echo "🗑️  To remove backup: git branch -D $BACKUP_BRANCH"
echo
echo "🎉 Git history rewrite completed successfully!"

