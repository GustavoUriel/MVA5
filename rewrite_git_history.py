#!/usr/bin/env python3
"""
Script to rewrite git commit history with professional messages and author information.
This script will create a comprehensive rewrite of all commits in the repository.
"""

import subprocess
import sys
import os

def run_git_command(command, check=True):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return "", e.stderr

def get_commit_list():
    """Get the list of all commits in reverse chronological order."""
    stdout, stderr = run_git_command("git log --oneline --reverse")
    commits = [line.split()[0] for line in stdout.split('\n') if line.strip()]
    return commits

def create_rewrite_script():
    """Create the git filter-branch script to rewrite commit messages and author info."""
    
    # New author information
    new_name = "Scientific Research Team"
    new_email = "research@microbiome-analysis.com"
    
    # Professional commit messages based on analysis
    commit_messages = [
        "feat: Initialize Microbiome Analysis Platform v1.0.0 with Flask architecture",
        "feat: Implement Google OAuth authentication and user management system", 
        "feat: Add dataset deletion functionality with confirmation dialogs",
        "feat: Implement file upload validation and data formatting",
        "feat: Add file deletion and management operations",
        "feat: Enhance dashboard UI with animated cards and statistics",
        "feat: Add file editing capabilities with modification tracking",
        "refactor: Remove auxiliary and temporary files from codebase",
        "feat: Implement table viewing and editing module with column preservation",
        "fix: Resolve filter conflicts in table edit due to style insertions",
        "feat: Remove CSV paste functionality and add file renaming",
        "feat: Enhance upload controls with multi-file support and result feedback",
        "feat: Implement file copying functionality",
        "feat: Organize files by type with count displays",
        "feat: Add data curation buttons and status tracking",
        "refactor: Begin major codebase restructuring for better maintainability",
        "refactor: Complete file operations module restructuring",
        "refactor: Complete file editing module restructuring", 
        "feat: Preserve column order and save schema in non-edit mode",
        "feat: Implement advanced column preservation with filtered row management",
        "feat: Complete file management module with bug fixes",
        "feat: Create analysis interface with data sources, parameters, and reports tabs",
        "feat: Implement initial analysis page with basic functionality",
        "refactor: Split pages into modules for improved maintainability",
        "refactor: Complete page modularization and separation",
        "feat: Add stratification functionality with mock data",
        "feat: Implement cluster representative selection feature",
        "feat: Add edges selector for network analysis",
        "feat: Populate analysis type configurations",
        "feat: Implement preliminary analysis saving functionality",
        "feat: Add analysis management (ABM) operations",
        "feat: Implement new analysis creation workflow",
        "fix: Implement dataset completion percentage and real-time progress updates",
        "feat: Add comprehensive analysis listing and management interface"
    ]
    
    # Create the filter-branch script
    script_content = f"""#!/bin/bash

# Git filter-branch script to rewrite commit messages and author information
# This script will rewrite the entire git history

export GIT_AUTHOR_NAME="{new_name}"
export GIT_AUTHOR_EMAIL="{new_email}"
export GIT_COMMITTER_NAME="{new_name}"  
export GIT_COMMITTER_EMAIL="{new_email}"

# Array of new commit messages
messages=(
    "{commit_messages[0]}"
    "{commit_messages[1]}"
    "{commit_messages[2]}"
    "{commit_messages[3]}"
    "{commit_messages[4]}"
    "{commit_messages[5]}"
    "{commit_messages[6]}"
    "{commit_messages[7]}"
    "{commit_messages[8]}"
    "{commit_messages[9]}"
    "{commit_messages[10]}"
    "{commit_messages[11]}"
    "{commit_messages[12]}"
    "{commit_messages[13]}"
    "{commit_messages[14]}"
    "{commit_messages[15]}"
    "{commit_messages[16]}"
    "{commit_messages[17]}"
    "{commit_messages[18]}"
    "{commit_messages[19]}"
    "{commit_messages[20]}"
    "{commit_messages[21]}"
    "{commit_messages[22]}"
    "{commit_messages[23]}"
    "{commit_messages[24]}"
    "{commit_messages[25]}"
    "{commit_messages[26]}"
    "{commit_messages[27]}"
    "{commit_messages[28]}"
    "{commit_messages[29]}"
    "{commit_messages[30]}"
    "{commit_messages[31]}"
    "{commit_messages[32]}"
    "{commit_messages[33]}"
)

# Counter for message index
counter=0

# Function to get the appropriate commit message
get_commit_message() {{
    if [ $counter -lt ${{#messages[@]}} ]; then
        echo "${{messages[$counter]}}"
        ((counter++))
    else
        echo "feat: Additional development improvements"
    fi
}}

# Use git filter-branch to rewrite the history
git filter-branch --msg-filter 'echo "$(get_commit_message)"' --env-filter '
    export GIT_AUTHOR_NAME="{new_name}"
    export GIT_AUTHOR_EMAIL="{new_email}"
    export GIT_COMMITTER_NAME="{new_name}"
    export GIT_COMMITTER_EMAIL="{new_email}"
' -- --all

echo "Git history rewrite completed successfully!"
echo "New author: {new_name} <{new_email}>"
echo "Total commits rewritten: ${{#messages[@]}}"
"""
    
    with open('rewrite_history.sh', 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod('rewrite_history.sh', 0o755)
    
    return 'rewrite_history.sh'

def main():
    """Main function to rewrite git history."""
    print("🔧 Microbiome Analysis Platform - Git History Rewrite Tool")
    print("=" * 60)
    
    # Check if we're in a git repository
    stdout, stderr = run_git_command("git rev-parse --git-dir", check=False)
    if stderr:
        print("❌ Error: Not in a git repository!")
        sys.exit(1)
    
    # Get current branch
    stdout, stderr = run_git_command("git branch --show-current")
    current_branch = stdout
    print(f"📍 Current branch: {current_branch}")
    
    # Get commit count
    stdout, stderr = run_git_command("git rev-list --count HEAD")
    commit_count = int(stdout)
    print(f"📊 Total commits to rewrite: {commit_count}")
    
    # Check for uncommitted changes
    stdout, stderr = run_git_command("git status --porcelain")
    if stdout.strip():
        print("⚠️  Warning: You have uncommitted changes!")
        print("Please commit or stash your changes before proceeding.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(1)
    
    # Create backup branch
    backup_branch = f"backup-before-rewrite-{int(time.time())}"
    print(f"💾 Creating backup branch: {backup_branch}")
    run_git_command(f"git branch {backup_branch}")
    
    # Create the rewrite script
    script_path = create_rewrite_script()
    print(f"📝 Created rewrite script: {script_path}")
    
    # Confirm before proceeding
    print("\n" + "=" * 60)
    print("⚠️  WARNING: This will rewrite the entire git history!")
    print("⚠️  This action cannot be easily undone!")
    print("⚠️  Make sure you have backups and no one else is working on this repository!")
    print("=" * 60)
    
    response = input("\nProceed with git history rewrite? (yes/NO): ")
    if response.lower() != 'yes':
        print("Aborted.")
        # Clean up
        run_git_command(f"git branch -D {backup_branch}", check=False)
        os.remove(script_path)
        sys.exit(0)
    
    # Execute the rewrite
    print("\n🚀 Starting git history rewrite...")
    print("This may take a few minutes depending on repository size...")
    
    try:
        stdout, stderr = run_git_command(f"bash {script_path}")
        print("✅ Git history rewrite completed successfully!")
        print(stdout)
        
        # Clean up the script
        os.remove(script_path)
        
        # Show the new history
        print("\n📋 New commit history:")
        print("-" * 40)
        stdout, stderr = run_git_command("git log --oneline --reverse")
        for i, line in enumerate(stdout.split('\n'), 1):
            if line.strip():
                print(f"{i:2d}. {line}")
        
        print(f"\n💾 Backup branch created: {backup_branch}")
        print("🔍 To view old history: git log --oneline backup-branch-name")
        print("🗑️  To remove backup: git branch -D backup-branch-name")
        
    except Exception as e:
        print(f"❌ Error during rewrite: {e}")
        print(f"🔄 Restoring from backup branch: {backup_branch}")
        run_git_command(f"git reset --hard {backup_branch}")
        sys.exit(1)

if __name__ == "__main__":
    import time
    main()

