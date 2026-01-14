# Git History Rewrite Script for Microbiome Analysis Platform
# PowerShell version for Windows

param(
    [switch]$Force
)

Write-Host "🔧 Microbiome Analysis Platform - Git History Rewrite" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if we're in a git repository
try {
    $gitDir = git rev-parse --git-dir 2>$null
    if (-not $gitDir) {
        Write-Host "❌ Error: Not in a git repository!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: Not in a git repository!" -ForegroundColor Red
    exit 1
}

# Get current branch
$currentBranch = git branch --show-current
Write-Host "📍 Current branch: $currentBranch" -ForegroundColor Green

# Get total commit count
$commitCount = git rev-list --count HEAD
Write-Host "📊 Total commits to rewrite: $commitCount" -ForegroundColor Green

# Check for uncommitted changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  Warning: You have uncommitted changes!" -ForegroundColor Yellow
    if (-not $Force) {
        $response = Read-Host "Continue anyway? (y/N)"
        if ($response -notmatch '^[Yy]$') {
            Write-Host "Aborted." -ForegroundColor Yellow
            exit 0
        }
    }
}

# Create backup branch
$backupBranch = "backup-before-rewrite-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "💾 Creating backup branch: $backupBranch" -ForegroundColor Blue
git branch $backupBranch

# New author information
$env:GIT_AUTHOR_NAME = "Scientific Research Team"
$env:GIT_AUTHOR_EMAIL = "research@microbiome-analysis.com"
$env:GIT_COMMITTER_NAME = "Scientific Research Team"
$env:GIT_COMMITTER_EMAIL = "research@microbiome-analysis.com"

Write-Host "👤 New author: $($env:GIT_AUTHOR_NAME) <$($env:GIT_AUTHOR_EMAIL)>" -ForegroundColor Green

# Professional commit messages array
$commitMessages = @(
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

Write-Host ""
Write-Host "⚠️  WARNING: This will rewrite the entire git history!" -ForegroundColor Red
Write-Host "⚠️  This action cannot be easily undone!" -ForegroundColor Red
Write-Host "⚠️  Make sure you have backups and no one else is working on this repository!" -ForegroundColor Red
Write-Host ""

if (-not $Force) {
    $response = Read-Host "Proceed with git history rewrite? (yes/NO)"
    if ($response -ne "yes") {
        Write-Host "Aborted." -ForegroundColor Yellow
        git branch -D $backupBranch 2>$null
        exit 0
    }
}

Write-Host ""
Write-Host "🚀 Starting git history rewrite..." -ForegroundColor Green
Write-Host "This may take a few minutes depending on repository size..." -ForegroundColor Yellow

# Create a temporary PowerShell script for the message filter
$messageFilterScript = @"
`$messages = @(
$(($commitMessages | ForEach-Object { "    `"$($_.Replace('"', '""'))`"" }) -join "`n")
)

if (Test-Path 'C:\temp\commit_counter.txt') {
    `$counter = [int](Get-Content 'C:\temp\commit_counter.txt')
} else {
    `$counter = 0
}

if (`$counter -lt `$messages.Length) {
    `$message = `$messages[`$counter]
} else {
    `$message = "feat: Additional development improvements"
}

`$counter++
Set-Content 'C:\temp\commit_counter.txt' -Value `$counter

Write-Output `$message
"@

# Create temp directory if it doesn't exist
if (-not (Test-Path 'C:\temp')) {
    New-Item -ItemType Directory -Path 'C:\temp' -Force | Out-Null
}

# Save the message filter script
Set-Content -Path 'C:\temp\message_filter.ps1' -Value $messageFilterScript

# Reset counter
Set-Content -Path 'C:\temp\commit_counter.txt' -Value "0"

# Use git filter-branch to rewrite the history
Write-Host "📝 Rewriting commit messages and author information..." -ForegroundColor Blue

try {
    # Set environment variables for git filter-branch
    $env:GIT_AUTHOR_NAME = "Scientific Research Team"
    $env:GIT_AUTHOR_EMAIL = "research@microbiome-analysis.com"
    $env:GIT_COMMITTER_NAME = "Scientific Research Team"
    $env:GIT_COMMITTER_EMAIL = "research@microbiome-analysis.com"
    
    # Run git filter-branch with PowerShell message filter
    git filter-branch --msg-filter "powershell.exe -File C:\temp\message_filter.ps1" --env-filter "export GIT_AUTHOR_NAME=Scientific Research Team; export GIT_AUTHOR_EMAIL=research@microbiome-analysis.com; export GIT_COMMITTER_NAME=Scientific Research Team; export GIT_COMMITTER_EMAIL=research@microbiome-analysis.com" -- --all
    
    Write-Host "✅ Git history rewrite completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error during rewrite: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔄 Restoring from backup branch: $backupBranch" -ForegroundColor Yellow
    git reset --hard $backupBranch
    exit 1
}

# Clean up temporary files
Remove-Item 'C:\temp\message_filter.ps1' -ErrorAction SilentlyContinue
Remove-Item 'C:\temp\commit_counter.txt' -ErrorAction SilentlyContinue

# Clean up filter-branch backup
Write-Host "🧹 Cleaning up filter-branch backup refs..." -ForegroundColor Blue
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

Write-Host ""
Write-Host "✅ Git history rewrite completed successfully!" -ForegroundColor Green
Write-Host ""

# Show the new history
Write-Host "📋 New commit history:" -ForegroundColor Cyan
Write-Host "----------------------" -ForegroundColor Cyan
$newHistory = git log --oneline --reverse
$counter = 1
foreach ($line in $newHistory) {
    if ($line.Trim()) {
        Write-Host "$($counter.ToString().PadLeft(2)) $line" -ForegroundColor White
        $counter++
    }
}

Write-Host ""
Write-Host "💾 Backup branch created: $backupBranch" -ForegroundColor Blue
Write-Host "🔍 To view old history: git log --oneline $backupBranch" -ForegroundColor Yellow
Write-Host "🗑️  To remove backup: git branch -D $backupBranch" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Git history rewrite completed successfully!" -ForegroundColor Green

