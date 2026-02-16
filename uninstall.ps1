# AI Commander - PowerShell Uninstaller
# Run: powershell -ExecutionPolicy Bypass -File uninstall.ps1

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "  AI Commander - UNINSTALLER" -ForegroundColor Red
Write-Host "  =================================" -ForegroundColor Red
Write-Host ""

$InstallDir = "$env:APPDATA\ai-commander"

# Check if installed
if (-not (Test-Path $InstallDir)) {
    Write-Host "AI Commander is not installed at $InstallDir" -ForegroundColor Yellow
    exit 0
}

# Remove PowerShell profile integration
Write-Host "Removing PowerShell profile integration..."
if (Test-Path $PROFILE) {
    try {
        $profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
        if ($profileContent -and $profileContent.Contains("AI Commander")) {
            # Remove the AI Commander block
            $lines = Get-Content $PROFILE
            $newLines = @()
            $inAiBlock = $false
            
            foreach ($line in $lines) {
                if ($line -match "# AI Commander - Natural language terminal commands") {
                    $inAiBlock = $true
                } elseif ($line -match "# AI Commander - END") {
                    $inAiBlock = $false
                    continue
                } elseif (-not $inAiBlock) {
                    $newLines += $line
                }
            }
            
            # Remove trailing empty lines
            while ($newLines.Count -gt 0 -and [string]::IsNullOrWhiteSpace($newLines[-1])) {
                $newLines = $newLines[0..($newLines.Count - 2)]
            }
            
            if ($newLines.Count -gt 0) {
                $newLines | Set-Content $PROFILE
            } else {
                Remove-Item $PROFILE -Force
            }
            Write-Host "[OK] Removed PowerShell profile integration" -ForegroundColor Green
        } else {
            Write-Host "[OK] No PowerShell profile integration found" -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARN] Could not update PowerShell profile: $_" -ForegroundColor Yellow
    }
}

# Remove CMD AutoRun registry entry
Write-Host "Removing CMD shell integration..."
try {
    $autoRun = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Command Processor" -Name AutoRun -ErrorAction SilentlyContinue
    if ($autoRun -and $autoRun.AutoRun -match "ai-commander") {
        Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Command Processor" -Name AutoRun -Force -ErrorAction SilentlyContinue
        Write-Host "[OK] Removed CMD AutoRun registry entry" -ForegroundColor Green
    } else {
        Write-Host "[OK] No CMD AutoRun registry entry found" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] Could not remove CMD AutoRun: $_" -ForegroundColor Yellow
}

# Remove installation directory with robust error handling
Write-Host ""
Write-Host "Removing installation directory: $InstallDir"

# Function to remove read-only attributes recursively
function Remove-ReadOnlyAttribute {
    param([string]$Path)
    
    try {
        Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                if ($_.Attributes -band [System.IO.FileAttributes]::ReadOnly) {
                    $_.Attributes = $_.Attributes -bxor [System.IO.FileAttributes]::ReadOnly
                }
            } catch {
                # Ignore individual file errors
            }
        }
    } catch {
        # Ignore errors in traversal
    }
}

# Attempt to remove read-only attributes first
Write-Host "Removing read-only attributes..."
Remove-ReadOnlyAttribute -Path $InstallDir

# Try to remove the directory
$maxRetries = 3
$retryCount = 0
$removed = $false

while ($retryCount -lt $maxRetries -and -not $removed) {
    try {
        if (Test-Path $InstallDir) {
            Remove-Item -Recurse -Force -Path $InstallDir -ErrorAction Stop
            $removed = $true
            Write-Host "[OK] Removed installation directory" -ForegroundColor Green
        } else {
            $removed = $true
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "[WARN] Removal attempt $retryCount failed, retrying..." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        } else {
            Write-Host "[ERROR] Could not fully remove installation directory" -ForegroundColor Red
            Write-Host "Some files may be locked or in use. Error: $_" -ForegroundColor Yellow
            
            # Try to remove individual files/folders that can be removed
            Write-Host ""
            Write-Host "Attempting partial cleanup..."
            try {
                Get-ChildItem -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue | 
                    Sort-Object -Property FullName -Descending | 
                    ForEach-Object {
                        try {
                            Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction Stop
                        } catch {
                            # Silently ignore files that can't be removed
                        }
                    }
                
                # Try to remove the main directory again
                if (Test-Path $InstallDir) {
                    Remove-Item -Path $InstallDir -Force -ErrorAction SilentlyContinue
                }
                
                if (-not (Test-Path $InstallDir)) {
                    Write-Host "[OK] Partial cleanup succeeded" -ForegroundColor Green
                    $removed = $true
                } else {
                    Write-Host ""
                    Write-Host "Please close any programs that might be using files in:" -ForegroundColor Yellow
                    Write-Host "  $InstallDir" -ForegroundColor Yellow
                    Write-Host ""
                    Write-Host "Then manually delete the folder or run this script again." -ForegroundColor Yellow
                }
            } catch {
                Write-Host "[ERROR] Partial cleanup failed: $_" -ForegroundColor Red
            }
        }
    }
}

# Done
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Uninstall Complete" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

if ($removed) {
    Write-Host "AI Commander has been successfully uninstalled." -ForegroundColor Green
} else {
    Write-Host "AI Commander has been partially uninstalled." -ForegroundColor Yellow
    Write-Host "Some files could not be removed automatically." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Open a new PowerShell window for changes to take effect." -ForegroundColor Cyan
Write-Host ""
