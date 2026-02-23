$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$template = if ($args.Length -ge 1) { $args[0] } else { "substrate/templates/wbs-codex-minimal.json" }
$state = "substrate/.governance/wbs-state.json"

if (-not (Test-Path $state)) {
  Write-Host "Initializing scaffold from $template..."
  bash -lc "./substrate/scripts/init-scaffold.sh '$template'"
}

Write-Host ""
Write-Host "Status"
python3 start.py --status

Write-Host ""
Write-Host "Briefing"
python3 substrate/.governance/wbs_cli.py briefing --format json

Write-Host ""
Write-Host "Ready"
python3 substrate/.governance/wbs_cli.py ready
