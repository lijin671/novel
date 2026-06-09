[CmdletBinding()]
param(
    [string[]]$Volume
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$volumes = if ($Volume -and $Volume.Count -gt 0) {
    $Volume
} else {
    docker volume ls -q
}

if (-not $volumes) {
    Write-Host "No Docker volumes found."
    exit 0
}

$results = foreach ($volumeName in $volumes) {
    $probe = docker run --rm -v "${volumeName}:/data" alpine sh -lc @'
if [ -f /data/18/docker/PG_VERSION ]; then
  echo "__MATCH__"
  du -sh /data/18/docker | cut -f1
  stat -c '%y' /data/18/docker/PG_VERSION
  stat -c '%y' /data/18/docker/postgresql.auto.conf 2>/dev/null || true
fi
'@

    if (-not $probe) {
        continue
    }

    $lines = $probe -split "`r?`n" | Where-Object { $_ -ne "" }
    if ($lines.Count -lt 2 -or $lines[0] -ne "__MATCH__") {
        continue
    }

    [pscustomobject]@{
        VolumeName            = $volumeName
        ClusterSize           = $lines[1]
        PgVersionMTime        = if ($lines.Count -ge 3) { $lines[2] } else { "" }
        AutoConfMTime         = if ($lines.Count -ge 4) { $lines[3] } else { "" }
    }
}

$results | Sort-Object AutoConfMTime -Descending | Format-Table -AutoSize
