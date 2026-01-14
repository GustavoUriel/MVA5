# PowerShell script to update commit messages
Write-Host "🔧 Updating commit messages..." -ForegroundColor Cyan

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

# Create a message filter script
$filterScript = @"
#!/bin/bash
counter=0
if [ -f /tmp/msg_counter ]; then
    counter=$(cat /tmp/msg_counter)
fi

messages=(
$(($messages | ForEach-Object { "    `"$($_.Replace('"', '""'))`"" }) -join "`n")
)

if [ $counter -lt ${#messages[@]} ]; then
    echo "${messages[$counter]}"
else
    echo "feat: Additional development improvements"
fi

echo $((counter + 1)) > /tmp/msg_counter
"@

# Save the filter script
Set-Content -Path "msg_filter.sh" -Value $filterScript

# Reset counter
Set-Content -Path "/tmp/msg_counter" -Value "0"

Write-Host "📝 Running git filter-branch for commit messages..." -ForegroundColor Blue

try {
    # Run git filter-branch to update commit messages
    git filter-branch -f --msg-filter "bash msg_filter.sh" -- --all
    
    Write-Host "✅ Commit messages updated successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error updating commit messages: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Clean up
Remove-Item "msg_filter.sh" -ErrorAction SilentlyContinue
Remove-Item "/tmp/msg_counter" -ErrorAction SilentlyContinue

Write-Host "🎉 Git history rewrite completed successfully!" -ForegroundColor Green



