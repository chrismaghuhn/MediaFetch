# Build Inno Setup installer after PyInstaller build
param(
    [string]$Version = "",
    [string]$IsccPath = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DistDir = Join-Path $Root "dist\MediaFetch"
$DistExe = Join-Path $DistDir "MediaFetch.exe"

if (-not (Test-Path $DistExe)) {
    Write-Host "dist\MediaFetch\MediaFetch.exe not found - running build first..."
    python (Join-Path $Root "scripts\build.py")
}

if (-not $Version) {
    $versionFile = Join-Path $Root "src\version.py"
    $line = Get-Content $versionFile | Where-Object { $_ -like '*__version__*' } | Select-Object -First 1
    if ($line -match '__version__\s*=\s*"(.+?)"') {
        $Version = $Matches[1]
    }
    else {
        Write-Error "Could not read __version__ from $versionFile"
    }
}

function Find-InnoSetupCompiler {
    param([string]$ExplicitPath)

    if ($ExplicitPath -and (Test-Path $ExplicitPath)) {
        return (Resolve-Path $ExplicitPath).Path
    }

    $candidates = @(
        $env:ISCC_PATH,
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    ) | Where-Object { $_ -and (Test-Path $_) }

    return $candidates | Select-Object -First 1
}

$Iscc = Find-InnoSetupCompiler -ExplicitPath $IsccPath

if (-not $Iscc) {
    Write-Error @"
Inno Setup 6 (ISCC.exe) not found.

Install options:
  winget install --id JRSoftware.InnoSetup --exact
  https://jrsoftware.org/isinfo.php

Or pass the compiler path:
  .\scripts\build_installer.ps1 -IsccPath `"$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe`"
"@
}

Write-Host "Building installer for version $Version..."
& $Iscc "/DMyAppVersion=$Version" (Join-Path $Root "installer\mediafetch.iss")

$Setup = Join-Path $Root "dist\MediaFetch-$Version-Setup.exe"
if (Test-Path $Setup) {
    Write-Host "Installer: $Setup"
}
else {
    Write-Error "Installer build failed"
}
