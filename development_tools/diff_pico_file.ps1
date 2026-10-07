# ------------------------------------------------------------
# Compare the currently open local_master_pico file
# with the corresponding file on the Pico.
#
# The Pico file is:
#   1. Downloaded to a temporary directory
#   2. Verified against the Pico SHA256
#   3. Opened beside the local file in VS Code Diff
#
# Usage:
#   diff_pico_file.ps1 <local-file>
# ------------------------------------------------------------

param (
    [Parameter(Mandatory=$true)]
    [string]$LocalFile
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

$python   = "F:\environments\env_micro_python\Scripts\python.exe"
$mpremote = "F:\environments\env_micro_python\Scripts\mpremote.exe"

# Load common configuration
. "$PSScriptRoot\config.ps1"

# $port is now available here
Write-Host "Using Pico on $port"

# ------------------------------------------------------------
# Verify that the Pico is available
# ------------------------------------------------------------
& $mpremote connect $port exec "print('PICO_OK')" >$null 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Pico is not available on $port."
    Write-Host "Make sure the Pico is connected and the port is not being used by Thonny."
    Write-Host ""
    exit 1
}


$masterDirectory = (
    Resolve-Path (Join-Path $PSScriptRoot "..\local_master_pico")
).Path

$downloadScript = Join-Path $PSScriptRoot "download_pico_file.py"

$tempDirectory = Join-Path $env:TEMP "pico_diff"

# ------------------------------------------------------------
# Resolve local file
# ------------------------------------------------------------

$LocalFile = (Resolve-Path $LocalFile).Path

# Make sure the file is inside local_master_pico
if (-not $LocalFile.StartsWith($masterDirectory)) {
    Write-Host ""
    Write-Host "ERROR: File is not inside local_master_pico"
    Write-Host ""
    Write-Host "File:"
    Write-Host "  $LocalFile"
    Write-Host ""
    exit 1
}


# ------------------------------------------------------------
# Determine relative Pico path
# ------------------------------------------------------------

$relativePath = $LocalFile.Substring($masterDirectory.Length)
$relativePath = $relativePath.TrimStart("\")

# Pico uses forward slashes
$picoPath = "/" + ($relativePath -replace "\\", "/")

# mpremote filesystem commands use :/
$mpremotePath = ":" + $picoPath


# ------------------------------------------------------------
# Create temporary directory
# ------------------------------------------------------------

if (-not (Test-Path $tempDirectory)) {
    New-Item -ItemType Directory -Path $tempDirectory | Out-Null
}

# Preserve filename for VS Code
$tempFile = Join-Path $tempDirectory ([System.IO.Path]::GetFileName($LocalFile))


# ------------------------------------------------------------
# Display comparison
# ------------------------------------------------------------

Write-Host ""
Write-Host "Local:"
Write-Host "  $LocalFile"

Write-Host ""
Write-Host "Pico:"
Write-Host "  $picoPath"

Write-Host ""


# ------------------------------------------------------------
# Download Pico file
# ------------------------------------------------------------

& $python $downloadScript $port $picoPath $tempFile

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Pico file download failed."
    exit 1
}


# ------------------------------------------------------------
# Get SHA256 of downloaded file
# ------------------------------------------------------------

$localHash = (
    Get-FileHash $tempFile -Algorithm SHA256
).Hash.ToLower()


# ------------------------------------------------------------
# Get SHA256 directly from Pico
# ------------------------------------------------------------

$picoHashOutput = & $mpremote connect $port fs sha256sum $mpremotePath
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Could not obtain Pico SHA256."
    exit 1
}

# mpremote output begins with the hexadecimal SHA256.
$picoHash = (
    $picoHashOutput |
    Select-String -Pattern "[0-9a-fA-F]{64}" |
    ForEach-Object { $_.Matches[0].Value }
)

if (-not $picoHash) {
    Write-Host ""
    Write-Host "ERROR: Could not parse Pico SHA256."
    Write-Host ""
    Write-Host $picoHashOutput
    exit 1
}

$picoHash = $picoHash.ToLower()


# ------------------------------------------------------------
# Verify download
# ------------------------------------------------------------

Write-Host ""
Write-Host "Downloaded SHA256:"
Write-Host "  $localHash"

Write-Host ""
Write-Host "Pico SHA256:"
Write-Host "  $picoHash"

Write-Host ""

if ($localHash -ne $picoHash) {

    Write-Host "ERROR: SHA256 mismatch."
    Write-Host "Downloaded file may be corrupted."
    Write-Host "VS Code diff cancelled."
    Write-Host ""

    exit 1
}

Write-Host "SHA256 verified."
Write-Host ""


# ------------------------------------------------------------
# Open VS Code Diff
# ------------------------------------------------------------

code --diff $LocalFile $tempFile