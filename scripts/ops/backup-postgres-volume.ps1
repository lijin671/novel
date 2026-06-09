[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceVolume,

    [string]$BackupVolume = ("{0}-backup-{1}" -f $SourceVolume, (Get-Date -Format "yyyyMMdd-HHmmss"))
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Creating backup volume: $BackupVolume"
docker volume create $BackupVolume | Out-Null

Write-Host "Copying PostgreSQL cluster data from $SourceVolume to $BackupVolume"
docker run --rm `
    -v "${SourceVolume}:/from:ro" `
    -v "${BackupVolume}:/to" `
    alpine sh -lc "cp -a /from/. /to/"

Write-Host "Backup complete."
Write-Host "SourceVolume = $SourceVolume"
Write-Host "BackupVolume = $BackupVolume"
