[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceVolume,

    [Parameter(Mandatory = $true)]
    [string]$TargetVolume,

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Ensuring target volume exists: $TargetVolume"
docker volume create $TargetVolume | Out-Null

$targetState = docker run --rm -v "${TargetVolume}:/data" alpine sh -lc @'
if [ -e /data/18/docker/PG_VERSION ]; then
  echo NON_EMPTY
elif [ -n "$(find /data -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
  echo NON_EMPTY
else
  echo EMPTY
fi
'@

if (($targetState -match "NON_EMPTY") -and -not $Force.IsPresent) {
    throw "Target volume '$TargetVolume' is not empty. Re-run with -Force only if you intend to overwrite it."
}

if ($Force.IsPresent) {
    Write-Host "Force mode enabled, clearing target volume before copy"
    docker run --rm -v "${TargetVolume}:/data" alpine sh -lc "rm -rf /data/*"
}

Write-Host "Copying PostgreSQL cluster data from $SourceVolume to $TargetVolume"
docker run --rm `
    -v "${SourceVolume}:/from:ro" `
    -v "${TargetVolume}:/to" `
    alpine sh -lc "cp -a /from/. /to/"

Write-Host "Migration complete."
Write-Host "SourceVolume = $SourceVolume"
Write-Host "TargetVolume = $TargetVolume"
