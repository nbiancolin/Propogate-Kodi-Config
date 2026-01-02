$Script:AdbPath = Join-Path $PSScriptRoot "..\adb\adb.exe"

function Ensure-Adb {
    if (Test-Path $Script:AdbPath) { return }

    Write-Host "ADB not found. Downloading platform-tools..."

    $zipUrl = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    $zipPath = Join-Path $PSScriptRoot "..\platform-tools.zip"
    $extractPath = Join-Path $PSScriptRoot ".."

    Invoke-WebRequest $zipUrl -OutFile $zipPath
    Expand-Archive $zipPath $extractPath -Force

    Rename-Item "$extractPath\platform-tools" "$extractPath\adb"
    Remove-Item $zipPath
}

function Connect-AndVerifyAdb {
    param (
        [Parameter(Mandatory)]
        [string]$Ip
    )

    & $Script:AdbPath disconnect | Out-Null
    & $Script:AdbPath connect $Ip | Out-Null

    $devices = & $Script:AdbPath devices
    if ($devices -match "$Ip\s+device") {
        return $true
    }

    throw "ADB connection to $Ip failed"
}

function Pull-KodiConfig {
    param ($Destination)

    & $Script:AdbPath pull `
        "/sdcard/Android/data/org.xbmc.kodi/files/.kodi" `
        $Destination `
        | Out-Null
}

function Push-KodiConfig {
    param ($Source)

    & $Script:AdbPath push `
        $Source `
        "/sdcard/Android/data/org.xbmc.kodi/files/" `
        | Out-Null
}

Export-ModuleMember -Function *
