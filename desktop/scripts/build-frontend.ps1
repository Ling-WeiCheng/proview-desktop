$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..\..')).Path
$frontendDir = Join-Path $repoRoot 'frontend'

if (-not (Test-Path (Join-Path $frontendDir 'node_modules'))) {
    & npm.cmd install --prefix $frontendDir
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to install frontend dependencies.'
    }
}

$env:PROVIEW_DESKTOP_BUILD = '1'
$env:PROVIEW_API_PORT = if ($env:PROVIEW_API_PORT) { $env:PROVIEW_API_PORT } else { '18765' }
$env:VITE_API_BASE_URL = if ($env:VITE_API_BASE_URL) { $env:VITE_API_BASE_URL } else { "http://127.0.0.1:$($env:PROVIEW_API_PORT)" }

& npm.cmd --prefix $frontendDir run build
if ($LASTEXITCODE -ne 0) {
    throw 'Frontend build failed.'
}

