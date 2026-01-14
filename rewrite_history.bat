@echo off
setlocal enabledelayedexpansion

echo 🔧 Microbiome Analysis Platform - Git History Rewrite
echo ==================================================

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Not in a git repository!
    exit /b 1
)

REM Get current branch
for /f %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo 📍 Current branch: %CURRENT_BRANCH%

REM Get total commit count
for /f %%i in ('git rev-list --count HEAD') do set COMMIT_COUNT=%%i
echo 📊 Total commits to rewrite: %COMMIT_COUNT%

REM Check for uncommitted changes
git status --porcelain | findstr /r ".*" >nul
if not errorlevel 1 (
    echo ⚠️  Warning: You have uncommitted changes!
    set /p response="Continue anyway? (y/N): "
    if /i not "%response%"=="y" (
        echo Aborted.
        exit /b 0
    )
)

REM Create backup branch
for /f %%i in ('powershell -command "Get-Date -Format 'yyyyMMdd-HHmmss'"') do set TIMESTAMP=%%i
set BACKUP_BRANCH=backup-before-rewrite-%TIMESTAMP%
echo 💾 Creating backup branch: %BACKUP_BRANCH%
git branch %BACKUP_BRANCH%

REM Set new author information
set GIT_AUTHOR_NAME=Scientific Research Team
set GIT_AUTHOR_EMAIL=research@microbiome-analysis.com
set GIT_COMMITTER_NAME=Scientific Research Team
set GIT_COMMITTER_EMAIL=research@microbiome-analysis.com

echo 👤 New author: %GIT_AUTHOR_NAME% ^<%GIT_AUTHOR_EMAIL%^>

echo.
echo ⚠️  WARNING: This will rewrite the entire git history!
echo ⚠️  This action cannot be easily undone!
echo ⚠️  Make sure you have backups and no one else is working on this repository!
echo.

set /p response="Proceed with git history rewrite? (yes/NO): "
if not "%response%"=="yes" (
    echo Aborted.
    git branch -D %BACKUP_BRANCH% >nul 2>&1
    exit /b 0
)

echo.
echo 🚀 Starting git history rewrite...
echo This may take a few minutes depending on repository size...

REM Create the commit message mapping
echo Creating commit message mapping...

REM Create a temporary script for message filtering
(
echo #!/bin/bash
echo # Git message filter script
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
echo if [ -f /tmp/commit_counter ]; then
echo     counter=$(cat /tmp/commit_counter^)
echo else
echo     counter=0
echo fi
echo.
echo if [ $counter -lt ${#messages[@]} ]; then
echo     echo "${messages[$counter]}"
echo else
echo     echo "feat: Additional development improvements"
echo fi
echo.
echo echo $((counter + 1^)) > /tmp/commit_counter
) > message_filter.sh

REM Create counter file
echo 0 > commit_counter

echo 📝 Rewriting commit messages and author information...

REM Run git filter-branch
git filter-branch ^
    --msg-filter "bash message_filter.sh" ^
    --env-filter "export GIT_AUTHOR_NAME=Scientific Research Team; export GIT_AUTHOR_EMAIL=research@microbiome-analysis.com; export GIT_COMMITTER_NAME=Scientific Research Team; export GIT_COMMITTER_EMAIL=research@microbiome-analysis.com" ^
    -- --all

if errorlevel 1 (
    echo ❌ Error during rewrite!
    echo 🔄 Restoring from backup branch: %BACKUP_BRANCH%
    git reset --hard %BACKUP_BRANCH%
    exit /b 1
)

REM Clean up temporary files
del message_filter.sh >nul 2>&1
del commit_counter >nul 2>&1

REM Clean up filter-branch backup
echo 🧹 Cleaning up filter-branch backup refs...
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

echo.
echo ✅ Git history rewrite completed successfully!
echo.

REM Show the new history
echo 📋 New commit history:
echo ----------------------
git log --oneline --reverse

echo.
echo 💾 Backup branch created: %BACKUP_BRANCH%
echo 🔍 To view old history: git log --oneline %BACKUP_BRANCH%
echo 🗑️  To remove backup: git branch -D %BACKUP_BRANCH%
echo.
echo 🎉 Git history rewrite completed successfully!

endlocal

