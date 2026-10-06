# ------------------------------------------------------------
# Run the active Python file on the Pico using mpremote mount
# ------------------------------------------------------------

param (
    [Parameter(Mandatory=$true)]
    [string]$localFile
)

# #uncomment the following for debugging
# param (
#     [string]$localFile = "F:\projects\tech_farm\tech_farm_nodes\local_master_pico\lib\pulse_generator\tools_pulse_generator.py"
# )

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
$mpremote = "F:\environments\env_micro_python\Scripts\mpremote.exe"

$port = "COM19"

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


# ------------------------------------------------------------
# Check that the file exists
# ------------------------------------------------------------

if (-not (Test-Path $localFile)) {
    Write-Host "File does not exist:"
    Write-Host $localFile
    exit 1
}


# ------------------------------------------------------------
# Make sure file is inside local_master_pico
# ------------------------------------------------------------

$fullLocalFile = (Resolve-Path $localFile).Path

if (-not $fullLocalFile.StartsWith($masterDirectory)) {
    Write-Host "File is not inside local_master_pico:"
    Write-Host $fullLocalFile
    exit 1
}


# ------------------------------------------------------------
# Determine path as seen through /remote
#
# Example:
#
# Local:
#   ...\local_master_pico\lib\pulse_generator\test.py
#
# Remote:
#   /remote/lib/pulse_generator/test.py
# ------------------------------------------------------------

$relativeFile = $fullLocalFile.Substring($masterDirectory.Length)
$relativeFile = $relativeFile.TrimStart("\")
$relativeFile = $relativeFile.Replace("\", "/")

$remoteFile = "/remote/$relativeFile"


Write-Host ""
Write-Host "Local file : $fullLocalFile"
Write-Host "Remote file: $remoteFile"
Write-Host ""


# ------------------------------------------------------------
# Command to execute on the Pico
# ------------------------------------------------------------

#$commands = "import sys; sys.path.insert(0, '/remote/lib'); exec(open('$remoteFile').read())"
$commands =  "import sys; '/remote/lib' in sys.path or sys.path.insert(0, '/remote/lib'); exec(open('$remoteFile').read())"

# ------------------------------------------------------------
# Mount local_master_pico and enter the REPL
#
# Ctrl+J = run the active file
# Ctrl+C = interrupt the running program
# Ctrl+] = exit mpremote
# ------------------------------------------------------------
Write-Host "bafagffa"
& $mpremote connect $port mount $masterDirectory repl --inject-code $commands