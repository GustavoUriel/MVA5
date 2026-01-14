# PowerShell script to update commit messages using git rebase
Write-Host "🔧 Updating commit messages using git rebase..." -ForegroundColor Cyan

# Array of professional commit messages
$messages = @(
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
)

# Get all commits in reverse order (oldest first)
$commits = git log --oneline --reverse | ForEach-Object { $_.Split(' ')[0] }

Write-Host "📊 Found $($commits.Count) commits to update" -ForegroundColor Green

# Create a rebase script
$rebaseScript = @"
#!/bin/bash
# Interactive rebase script for updating commit messages

# Set the editor to a script that will update each commit message
export GIT_SEQUENCE_EDITOR="sed -i 's/^pick/edit/g'"

# Start interactive rebase from the beginning
git rebase -i --root
"@

# Save the rebase script
Set-Content -Path "rebase_script.sh" -Value $rebaseScript

Write-Host "📝 Created rebase script" -ForegroundColor Blue

# Let's try a different approach - use git filter-branch with a simpler method
Write-Host "🔄 Trying alternative approach with git filter-branch..." -ForegroundColor Yellow

# Create a simple message replacement script
$replaceScript = @"
#!/bin/bash
# Simple message replacement based on commit hash patterns

case `$GIT_COMMIT in
    7687aeb*) echo "feat: Initialize Microbiome Analysis Platform v1.0.0 with Flask architecture" ;;
    c755fb2*) echo "feat: Implement Google OAuth authentication and user management system" ;;
    3f46399*) echo "feat: Add dataset deletion functionality with confirmation dialogs" ;;
    08b772c*) echo "feat: Implement file upload validation and data formatting" ;;
    3f8bb3e*) echo "feat: Add file deletion and management operations" ;;
    543ea7a*) echo "feat: Enhance dashboard UI with animated cards and statistics" ;;
    8ef3f4a*) echo "feat: Add file editing capabilities with modification tracking" ;;
    5e402e9*) echo "refactor: Remove auxiliary and temporary files from codebase" ;;
    298d6d7*) echo "feat: Implement table viewing and editing module with column preservation" ;;
    63b09d0*) echo "fix: Resolve filter conflicts in table edit due to style insertions" ;;
    5b58893*) echo "feat: Remove CSV paste functionality and add file renaming" ;;
    ef55dad*) echo "feat: Enhance upload controls with multi-file support and result feedback" ;;
    73b01d3*) echo "feat: Implement file copying functionality" ;;
    feee15a*) echo "feat: Organize files by type with count displays" ;;
    1c9d556*) echo "feat: Add data curation buttons and status tracking" ;;
    35f4670*) echo "refactor: Begin major codebase restructuring for better maintainability" ;;
    46f5202*) echo "refactor: Complete file operations module restructuring" ;;
    38e963d*) echo "refactor: Complete file editing module restructuring" ;;
    f651b73*) echo "feat: Preserve column order and save schema in non-edit mode" ;;
    b955acd*) echo "feat: Implement advanced column preservation with filtered row management" ;;
    9892803*) echo "feat: Complete file management module with bug fixes" ;;
    84a0b05*) echo "feat: Create analysis interface with data sources, parameters, and reports tabs" ;;
    c85f1c6*) echo "feat: Implement initial analysis page with basic functionality" ;;
    028fe2b*) echo "refactor: Split pages into modules for improved maintainability" ;;
    1d236c5*) echo "refactor: Complete page modularization and separation" ;;
    7cff37d*) echo "feat: Add stratification functionality with mock data" ;;
    a0d76c9*) echo "feat: Implement cluster representative selection feature" ;;
    0eaa0e2*) echo "feat: Add edges selector for network analysis" ;;
    810b14b*) echo "feat: Populate analysis type configurations" ;;
    8abf04d*) echo "feat: Implement preliminary analysis saving functionality" ;;
    a40ed1c*) echo "feat: Add analysis management (ABM) operations" ;;
    dc2594d*) echo "feat: Implement new analysis creation workflow" ;;
    87f373b*) echo "fix: Implement dataset completion percentage and real-time progress updates" ;;
    1c5b6ab*) echo "feat: Add comprehensive analysis listing and management interface" ;;
    *) echo "feat: Additional development improvements" ;;
esac
"@

# Save the replacement script
Set-Content -Path "commit_replacer.sh" -Value $replaceScript

Write-Host "📝 Created commit message replacement script" -ForegroundColor Blue

# Run git filter-branch with the replacement script
Write-Host "🚀 Running git filter-branch with message replacement..." -ForegroundColor Green

try {
    git filter-branch -f --msg-filter "bash commit_replacer.sh" -- --all
    Write-Host "✅ Commit messages updated successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error updating commit messages: $($_.Exception.Message)" -ForegroundColor Red
}

# Clean up
Remove-Item "rebase_script.sh" -ErrorAction SilentlyContinue
Remove-Item "commit_replacer.sh" -ErrorAction SilentlyContinue

Write-Host "🎉 Git history rewrite completed!" -ForegroundColor Green



