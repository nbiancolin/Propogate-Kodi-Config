Import-Module "$PSScriptRoot\modules\adb.psm1" -Force

Ensure-Adb

$selection = & "$PSScriptRoot\select-firesticks.ps1"

$src = $selection.Source
$destinations = $selection.Destinations

$tempDir = Join-Path $PSScriptRoot "temp"

if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item $tempDir -ItemType Directory | Out-Null

Write-Host "`nConnecting to SOURCE: $($src.Name)"

Connect-AndVerifyAdb $src.IP
Pull-KodiConfig $tempDir

foreach ($dst in $destinations) {
    Write-Host "`nTransferring to: $($dst.Name)"

    Connect-AndVerifyAdb $dst.IP
    Push-KodiConfig $tempDir
}

Write-Host "`nKodi config successfully transferred!"
