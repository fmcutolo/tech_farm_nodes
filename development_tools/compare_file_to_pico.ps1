# ------------------------------------------------------------
# Compare the active local MicroPython file with the
# corresponding file on the Pico.
#
# Results:
#
#   SAME
#   DIFFERENT
#   DOESN'T EXIST ON PICO
#
# Example:
#
# Local:
#   local_master_pico\lib\pulse_generator\pulse_generator.py
#
# Pico:
#   /lib/pulse_generator/pulse_generator.py
# ------------------------------------------------------------


param (
    [Parameter(Mandatory=$true)]
    [string]$localFile
)

# #uncomment the following for debugging
# param (
#     [string]$localFile = "F:\projects\tech_farm\tech_farm_nodes\local_master_pico\lib\pulse_generator\pulse_generator.py"
# )


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

# Load common configuration
. "$PSScriptRoot\config.ps1"

# $port is now available here
Write-Host "Using Pico on $port"

$python = "F:\environments\env_micro_python\Scripts\python.exe"

$downloadScript = Join-Path $PSScriptRoot "download_pico_file.py"

$masterDirectory = (
    Resolve-Path (Join-Path $PSScriptRoot "..\local_master_pico")
).Path


# ------------------------------------------------------------
# Make sure Pico is available
# ------------------------------------------------------------

#& $python $downloadScript $port "/" "$env:TEMP\pico_test" 2>$null | Out-Null

# The test above isn't appropriate for a directory, so instead
# use mpremote simply to verify the connection.

$mpremote = "F:\environments\env_micro_python\Scripts\mpremote.exe"

& $mpremote connect $port fs ls ":/" 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Pico is not available on $port"
    exit 1
}


# ------------------------------------------------------------
# Get full path of active local file
# ------------------------------------------------------------
$fileName = $localFile
$localFile = (Resolve-Path $localFile).Path


# ------------------------------------------------------------
# Make sure file belongs to local_master_pico
# ------------------------------------------------------------

if (-not $localFile.StartsWith($masterDirectory)) {
    Write-Host "File is not inside local_master_pico"
    exit 1
}


# ------------------------------------------------------------
# Determine corresponding Pico path
# ------------------------------------------------------------

$relativePath = $localFile.Substring($masterDirectory.Length)

$picoFile = $relativePath.Replace("\", "/")

if (-not $picoFile.StartsWith("/")) {
    $picoFile = "/" + $picoFile
}


# ------------------------------------------------------------
# Create temporary directory
# ------------------------------------------------------------

$tempDirectory = Join-Path $env:TEMP "pico_compare"

New-Item `
    -ItemType Directory `
    -Force `
    -Path $tempDirectory | Out-Null


$tempFile = Join-Path `
    $tempDirectory `
    ([System.IO.Path]::GetFileName($localFile))


# ------------------------------------------------------------
# Download corresponding Pico file
# ------------------------------------------------------------

& $python $downloadScript $port $picoFile $tempFile 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {

    Write-Host "*`n$relativePath DOESN'T EXIST ON PICO`n*"

    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force
    }

    exit 0
}


# ------------------------------------------------------------
# Compare SHA256 hashes
# ------------------------------------------------------------

$localHash = (
    Get-FileHash $localFile -Algorithm SHA256
).Hash

$picoHash = (
    Get-FileHash $tempFile -Algorithm SHA256
).Hash


if ($localHash -eq $picoHash) {
    Write-Host "*`n$relativePath is the SAME`n*"
}
else {
    Write-Host "*`n$relativePath is DIFFERENT`n*"
}


# ------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------

Remove-Item $tempFile -Force
