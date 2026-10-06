# ------------------------------------------------------------
# Copy new or changed files from local_master_pico to Pico
#
# Copies:
#   LOCAL ONLY
#   DIFFERENT
#
# Does NOT:
#   Copy SAME files
#   Delete PICO ONLY files
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


function Ensure-PicoDirectory {

    param (
        [string]$directory
    )

    if ([string]::IsNullOrEmpty($directory)) {
        return
    }

    $parts = $directory.Split("/")

    $currentPath = ""

    foreach ($part in $parts) {

        if ($part -eq "") {
            continue
        }

        $currentPath += "/" + $part

        # mkdir will fail if the directory already exists.
        # Suppress that error.
        & $mpremote connect $port fs mkdir ":$currentPath" 2>$null
    }
}
# ------------------------------------------------------------
# Get local files
# ------------------------------------------------------------

$localFiles = Get-ChildItem $localDirectory -File -Recurse

$localPaths = @()

foreach ($file in $localFiles) {

    $relativePath = $file.FullName.Substring($localDirectory.Length)

    $relativePath = $relativePath.TrimStart("\")

    # Use Pico-style paths internally.
    $relativePath = $relativePath.Replace("\", "/")

    $localPaths += $relativePath
}


# ------------------------------------------------------------
# Get Pico files
# ------------------------------------------------------------

$picoResult = & $mpremote connect $port run $listPicoFiles

$picoPaths = @()

foreach ($path in $picoResult) {

    $path = $path.Trim()

    if ($path.StartsWith("/")) {

        $path = $path.TrimStart("/")

        $picoPaths += $path
    }
}


# ------------------------------------------------------------
# Display header
# ------------------------------------------------------------

Write-Host ""
Write-Host "Updating Pico from local master"
Write-Host ""
Write-Host "Local Master: $localDirectory"
Write-Host "Pico:         ${port}:/"
Write-Host ""


# ------------------------------------------------------------
# Copy files
# ------------------------------------------------------------

$copyCount = 0


foreach ($relativePath in $localPaths) {

    $localFile = Join-Path $localDirectory $relativePath

    $picoExists = $relativePath -in $picoPaths

    $copyFile = $false


    # --------------------------------------------------------
    # File doesn't exist on Pico
    # --------------------------------------------------------

    if (-not $picoExists) {

        Write-Host ("{0,-55} NEW" -f $relativePath)

        $copyFile = $true
    }


    # --------------------------------------------------------
    # File exists on Pico -- compare hashes
    # --------------------------------------------------------

    else {

        $localHash = (Get-FileHash $localFile -Algorithm SHA256).Hash

        $picoFile = ":/$relativePath"

        $result = & $mpremote connect $port fs sha256sum $picoFile 2>$null

        $picoHash = $result[1].Trim()


        if ($localHash -ne $picoHash) {

            Write-Host ("{0,-55} CHANGED" -f $relativePath)

            $copyFile = $true
        }
        else {

            Write-Host ("{0,-55} SAME" -f $relativePath)
        }
    }


    # --------------------------------------------------------
    # Copy new/changed file
    # --------------------------------------------------------

    if ($copyFile) {

        # Determine Pico destination directory.

        $lastSlash = $relativePath.LastIndexOf("/")

        if ($lastSlash -ge 0) {

            $picoDirectory = $relativePath.Substring(0, $lastSlash)

            # mkdir with -p creates parent directories as needed.
            Ensure-PicoDirectory $picoDirectory        }


        $picoFile = ":/$relativePath"

        Write-Host ("    -> copying to {0}" -f $picoFile)

        & $mpremote connect $port fs cp $localFile $picoFile

        $copyCount++
    }
}


# ------------------------------------------------------------
# Report Pico-only files
# ------------------------------------------------------------

foreach ($relativePath in $picoPaths) {

    if ($relativePath -notin $localPaths) {

        Write-Host ("{0,-55} PICO ONLY - not changed" -f $relativePath)
    }
}


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

Write-Host ""
Write-Host "------------------------------------------------------------"

if ($copyCount -eq 0) {

    Write-Host "Pico is already up to date."
}
else {

    Write-Host "$copyCount file(s) copied to Pico."
}

Write-Host ""