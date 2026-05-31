# Build Inno Setup installer after PyInstaller build
param(
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DistDir = Join-Path $Root "dist\MediaFetch"
$DistExe = Join-Path $DistDir "MediaFetch.exe"

if (-not (Test-Path $DistExe)) {
    Write-Host "dist\MediaFetch\MediaFetch.exe not found — running build first..."
    python (Join-Path $Root "scripts\build.py")
}

if (-not $Version) {
    $VersionLine = Select-String -Path (Join-Path $Root "src\version.py") -Pattern '__version__\s*=\s*"([^"]+)"'
    $Version = $VersionLine.Matches.Groups[1].Value
}

$Iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $Iscc) {
    Write-Error "Inno Setup 6 (ISCC.exe) not found. Install from https://jrsoftware.org/isinfo.php"
}

Write-Host "Building installer for version $Version..."
& $Iscc "/DMyAppVersion=$Version" (Join-Path $Root "installer\mediafetch.iss")

$Setup = Join-Path $Root "dist\MediaFetch-$Version-Setup.exe"
if (Test-Path $Setup) {
    Write-Host "Installer: $Setup"
} else {
    Write-Error "Installer build failed"
}
