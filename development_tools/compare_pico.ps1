# ------------------------------------------------------------
# Compare local MicroPython master files with files on a Pico
#
# Directory structure:
#
#   tech_farm_nodes/
#       compare_pico.ps1
#       list_pico_files.py
#       local_pico/
#
# Reports:
#   SAME
#   DIFFERENT
#   LOCAL ONLY
#   PICO ONLY
# ------------------------------------------------------------


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

$localDirectory = (Resolve-Path (Join-Path $PSScriptRoot "..\local_master_pico")).Path
$listPicoFiles  = Join-Path $PSScriptRoot "list_pico_files.py"
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



# ------------------------------------------------------------
# Get local .py files
# ------------------------------------------------------------

#$localFiles = Get-ChildItem $localDirectory -Filter "*.py" -File -Recurse
$localFiles = Get-ChildItem $localDirectory -File -Recurse

$localPaths = @()


foreach ($file in $localFiles) {

    # Get path relative to local_pico.

    $relativePath = $file.FullName.Substring($localDirectory.Length)

    $relativePath = $relativePath.TrimStart("\")


    # Internally use forward slashes so the local paths have
    # the same format as the Pico paths.

    $relativePath = $relativePath.Replace("\", "/")


    $localPaths += $relativePath
}


# ------------------------------------------------------------
# Get Pico .py files
# ------------------------------------------------------------

$picoResult = & $mpremote connect $port run $listPicoFiles

$picoPaths = @()


foreach ($path in $picoResult) {

    $path = $path.Trim()


    # list_pico_files.py returns paths such as:
    #
    # /main.py
    # /lib/bus/i2c_bus.py
    #
    # Remove the leading slash so they match $localPaths.

    # if ($path.EndsWith(".py")) {

    #     $path = $path.TrimStart("/")

    #     $picoPaths += $path
    # }

    if ($path.StartsWith("/")) {

        $path = $path.TrimStart("/")
    
        $picoPaths += $path
    }
}


# ------------------------------------------------------------
# Create combined list
# ------------------------------------------------------------

$allPaths = $localPaths + $picoPaths |
    Sort-Object -Unique


# ------------------------------------------------------------
# Display comparison information
# ------------------------------------------------------------

Write-Host ""
Write-Host "Comparing local master with Pico"
Write-Host ""
Write-Host "Local Master: $localDirectory"
Write-Host "Pico:  ${port}:/"
Write-Host ""


# ------------------------------------------------------------
# Compare files
# ------------------------------------------------------------

$differenceCount = 0


foreach ($relativePath in $allPaths) {

    $localExists = $relativePath -in $localPaths
    $picoExists  = $relativePath -in $picoPaths


    # --------------------------------------------------------
    # Local only
    # --------------------------------------------------------

    if ($localExists -and -not $picoExists) {

        Write-Host ("{0,-55} LOCAL ONLY" -f $relativePath)

        $differenceCount++

        continue
    }


    # --------------------------------------------------------
    # Pico only
    # --------------------------------------------------------

    if ($picoExists -and -not $localExists) {

        Write-Host ("{0,-55} PICO ONLY" -f $relativePath)

        $differenceCount++

        continue
    }


    # --------------------------------------------------------
    # File exists in both places.
    # Calculate local SHA256.
    # --------------------------------------------------------

    $localFile = Join-Path $localDirectory $relativePath

    $localHash = (Get-FileHash $localFile -Algorithm SHA256).Hash


    # --------------------------------------------------------
    # Calculate Pico SHA256.
    # --------------------------------------------------------

    $picoFile = ":/$relativePath"

    $result = & $mpremote connect $port fs sha256sum $picoFile 2>$null


    # mpremote 1.25.0 returns:
    #
    # sha256sum :/path/file.py
    # <hash>

    $picoHash = $result[1].Trim()


    # --------------------------------------------------------
    # Compare hashes
    # --------------------------------------------------------

    if ($localHash -eq $picoHash) {

        Write-Host ("{0,-55} SAME" -f $relativePath)

    }
    else {

        Write-Host ("{0,-55} DIFFERENT" -f $relativePath)

        $differenceCount++
    }
}


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

Write-Host ""
Write-Host "------------------------------------------------------------"


if ($differenceCount -eq 0) {

    Write-Host "All files are identical."

}
else {

    Write-Host "$differenceCount difference(s) found."
}


Write-Host ""