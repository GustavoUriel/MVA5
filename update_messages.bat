@echo off
setlocal enabledelayedexpansion

echo 🔧 Updating commit messages...

REM Create the message filter script
(
echo #!/bin/bash
echo counter=0
echo if [ -f /tmp/message_counter ]; then
echo     counter=$(cat /tmp/message_counter^)
echo fi
echo.
echo messages=(
echo "feat: Initialize Microbiome Analysis Platform v1.0.0 with Flask architecture"
echo "feat: Implement Google OAuth authentication and user management system"
echo "feat: Add dataset deletion functionality with confirmation dialogs"
echo "feat: Implement file upload validation and data formatting"
echo "feat: Add file deletion and management operations"
echo "feat: Enhance dashboard UI with animated cards and statistics"
echo "feat: Add file editing capabilities with modification tracking"
echo "refactor: Remove auxiliary and temporary files from codebase"
echo "feat: Implement table viewing and editing module with column preservation"
echo "fix: Resolve filter conflicts in table edit due to style insertions"
echo "feat: Remove CSV paste functionality and add file renaming"
echo "feat: Enhance upload controls with multi-file support and result feedback"
echo "feat: Implement file copying functionality"
echo "feat: Organize files by type with count displays"
echo "feat: Add data curation buttons and status tracking"
echo "refactor: Begin major codebase restructuring for better maintainability"
echo "refactor: Complete file operations module restructuring"
echo "refactor: Complete file editing module restructuring"
echo "feat: Preserve column order and save schema in non-edit mode"
echo "feat: Implement advanced column preservation with filtered row management"
echo "feat: Complete file management module with bug fixes"
echo "feat: Create analysis interface with data sources, parameters, and reports tabs"
echo "feat: Implement initial analysis page with basic functionality"
echo "refactor: Split pages into modules for improved maintainability"
echo "refactor: Complete page modularization and separation"
echo "feat: Add stratification functionality with mock data"
echo "feat: Implement cluster representative selection feature"
echo "feat: Add edges selector for network analysis"
echo "feat: Populate analysis type configurations"
echo "feat: Implement preliminary analysis saving functionality"
echo "feat: Add analysis management (ABM) operations"
echo "feat: Implement new analysis creation workflow"
echo "fix: Implement dataset completion percentage and real-time progress updates"
echo "feat: Add comprehensive analysis listing and management interface"
echo ^)
echo.
echo if [ $counter -lt ${#messages[@]} ]; then
echo     echo "${messages[$counter]}"
echo else
echo     echo "feat: Additional development improvements"
echo fi
echo.
echo echo $((counter + 1^)) > /tmp/message_counter
) > message_filter.sh

REM Reset counter
echo 0 > /tmp/message_counter

echo 📝 Running git filter-branch for commit messages...

REM Run git filter-branch
git filter-branch --msg-filter "bash message_filter.sh" -- --all

REM Clean up
del message_filter.sh
del /tmp/message_counter 2>nul
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

echo ✅ Commit messages updated successfully!
echo 🎉 Git history rewrite completed!

