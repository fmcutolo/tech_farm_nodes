param (
    [Parameter(Mandatory=$true)]
    [string]$localFile
)

# #uncomment the following for debugging
# param (
#     [string]$localFile = "F:\projects\tech_farm\tech_farm_nodes\local_master_pico\lib\pulse_generator\pulse_generator.py"
# )



$port = "COM19"
$mpremote = "F:\environments\env_micro_python\Scripts\mpremote.exe"

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


# Root of the files that mirror the Pico
$masterRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\local_master_pico")).Path

# Resolve active file
$localFile = (Resolve-Path $localFile).Path

Write-Host ""
Write-Host "Local file:"
Write-Host "  $localFile"

# Make sure the selected file belongs to local_master_pico
if (-not $localFile.StartsWith($masterRoot)) {
    Write-Host ""
    Write-Host "ERROR: File is not inside local_master_pico"
    exit 1
}

# Determine relative path
$relativePath = $localFile.Substring($masterRoot.Length).TrimStart("\")

# Convert Windows separators to Pico separators
$picoFile = ":/" + $relativePath.Replace("\", "/")

Write-Host ""
Write-Host "Pico file:"
Write-Host "  $picoFile"
Write-Host ""

# ------------------------------------------------------------
# Create Pico destination directories if necessary
# ------------------------------------------------------------

$picoPath = $relativePath.Replace("\", "/")

$lastSlash = $picoPath.LastIndexOf("/")

if ($lastSlash -ge 0) {
    $picoDirectory = $picoPath.Substring(0, $lastSlash)
}
else {
    $picoDirectory = ""
}

if ($picoDirectory) {

    # $currentDirectory = ""

    # foreach ($directory in $picoDirectory.Split("/")) {

    #     $currentDirectory += "/" + $directory

    #     # mkdir will report an error if the directory already exists,
    #     # so suppress that output.
    #     & $mpremote connect $port fs mkdir ":$currentDirectory" 2>$null
    # }

    $currentDirectory = ""

    foreach ($directory in $picoDirectory.Split("/")) {
    
        $currentDirectory += "/" + $directory
    
        $code = @"
import os
try:
    os.stat('$currentDirectory')
except OSError:
    os.mkdir('$currentDirectory')
"@
    
        & $mpremote connect $port exec $code
    }








}

# Copy to Pico
& $mpremote connect $port fs cp $localFile $picoFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Copy complete."
}
else {
    Write-Host ""
    Write-Host "ERROR: Copy failed."
}