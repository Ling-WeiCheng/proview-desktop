param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BuilderArgs
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopDir = (Resolve-Path (Join-Path $scriptDir '..')).Path

if (-not $env:ELECTRON_MIRROR) {
    $env:ELECTRON_MIRROR = 'https://npmmirror.com/mirrors/electron/'
}

if (-not $env:ELECTRON_BUILDER_BINARIES_MIRROR) {
    $env:ELECTRON_BUILDER_BINARIES_MIRROR = 'https://npmmirror.com/mirrors/electron-builder-binaries/'
}

Push-Location $desktopDir
try {
    & npx.cmd electron-builder @BuilderArgs
    if ($LASTEXITCODE -ne 0) {
        throw 'Electron packaging failed.'
    }
} finally {
    Pop-Location
}
