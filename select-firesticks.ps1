param (
    [string]$ConfigPath = "config.ini"
)

if (!(Test-Path $ConfigPath)) {
    throw "config.ini not found"
}

$firesticks = @()

Get-Content $ConfigPath | ForEach-Object {
    if ($_ -match '^\s*([^=]+)=([\d\.]+)\s*$') {
        $firesticks += [pscustomobject]@{
            Name = $matches[1]
            IP   = $matches[2]
        }
    }
}

if ($firesticks.Count -eq 0) {
    throw "No firesticks found in config.ini"
}

Write-Host "`nAvailable Fire Sticks:`n"

for ($i = 0; $i -lt $firesticks.Count; $i++) {
    Write-Host "$($i+1)) $($firesticks[$i].Name) ($($firesticks[$i].IP))"
}

$srcIndex = Read-Host "`nSelect SOURCE number"
$src = $firesticks[$srcIndex - 1]

$dstInput = Read-Host "Select DESTINATIONS (comma-separated numbers)"
$dstIndices = $dstInput -split ',' | ForEach-Object { $_.Trim() }

$destinations = foreach ($i in $dstIndices) {
    if ($i -eq $srcIndex) {
        throw "Destination cannot be the source"
    }
    $firesticks[$i - 1]
}

[pscustomobject]@{
    Source       = $src
    Destinations = $destinations
}
