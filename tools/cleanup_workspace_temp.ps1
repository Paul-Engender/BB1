[CmdletBinding()]
param(
    [switch]$UseAclFallback = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

$targets = @(
    (Join-Path $repoRoot ".tmp_tests"),
    (Join-Path $repoRoot "tmp_work"),
    (Join-Path $repoRoot "tests/_tmp*"),
    (Join-Path $repoRoot "dist/tmp_load_*"),
    (Join-Path $repoRoot "dist/runtime2_support_verify_*"),
    (Join-Path $repoRoot "Untitled document.gdoc")
)

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-Matches {
    param([Parameter(Mandatory = $true)][string]$Pattern)

    if ($Pattern.Contains("*")) {
        return @(Get-ChildItem -Path $Pattern -Force -ErrorAction SilentlyContinue)
    }

    if (Test-Path -LiteralPath $Pattern) {
        return @((Get-Item -LiteralPath $Pattern -Force -ErrorAction SilentlyContinue))
    }

    return @()
}

function Remove-Normal {
    param([Parameter(Mandatory = $true)][string]$Path)

    Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
}

function Remove-WithAclFallback {
    param([Parameter(Mandatory = $true)][string]$Path)

    $userPrincipal = "$env:USERDOMAIN\$env:USERNAME"

    & takeown.exe /F $Path /R /D Y 2>$null | Out-Null
    & icacls.exe $Path /grant "$($userPrincipal):(OI)(CI)F" /T /C 2>$null | Out-Null
    Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
}

$failed = New-Object System.Collections.Generic.List[string]
$removed = New-Object System.Collections.Generic.List[string]

foreach ($target in $targets) {
    $matches = Get-Matches -Pattern $target
    foreach ($item in $matches) {
        if (-not $item) {
            continue
        }

        $fullPath = $item.FullName
        try {
            Remove-Normal -Path $fullPath
            $removed.Add($fullPath) | Out-Null
            Write-Output "Removed: $fullPath"
        }
        catch {
            Write-Output "Normal remove failed: $fullPath :: $($_.Exception.Message)"
            $failed.Add($fullPath) | Out-Null
        }
    }
}

if ($UseAclFallback -and $failed.Count -gt 0) {
    $retry = @($failed | Select-Object -Unique)
    $failed = New-Object System.Collections.Generic.List[string]

    foreach ($path in $retry) {
        try {
            if (-not (Test-Path -LiteralPath $path)) {
                continue
            }
            Remove-WithAclFallback -Path $path
            $removed.Add($path) | Out-Null
            Write-Output "Removed with fallback: $path"
        }
        catch {
            Write-Output "Fallback remove failed: $path :: $($_.Exception.Message)"
            $failed.Add($path) | Out-Null
        }
    }
}

if ($removed.Count -eq 0) {
    Write-Output "No cleanup targets removed."
}

if ($failed.Count -gt 0) {
    Write-Output "Unresolved paths:"
    foreach ($path in ($failed | Select-Object -Unique)) {
        Write-Output "- $path"
    }

    if (-not (Test-IsAdministrator)) {
        Write-Output "Hint: run this script from an Administrator PowerShell session for ownership reset on locked ACL trees."
    }

    exit 1
}

Write-Output "Cleanup completed successfully."
exit 0