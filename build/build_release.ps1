# MediaFetch release build — exe + optional installer
param(
    [switch]$SkipFfmpeg,
    [switch]$Installer
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BinDir = Join-Path $Root "resources\bin"

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

if (-not $SkipFfmpeg) {
    $FfmpegPath = Join-Path $BinDir "ffmpeg.exe"
    if (-not (Test-Path $FfmpegPath)) {
        Write-Host "Downloading FFmpeg..."
        $FfmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        $TempZip = Join-Path $env:TEMP "ffmpeg.zip"
        Invoke-WebRequest -Uri $FfmpegUrl -OutFile $TempZip
        $TempExtract = Join-Path $env:TEMP "ffmpeg_extract"
        Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
        $FfmpegSrc = Get-ChildItem -Path $TempExtract -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
        Copy-Item $FfmpegSrc.FullName -Destination $FfmpegPath
        Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
        Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
    }
}

$YtdlpPath = Join-Path $BinDir "yt-dlp.exe"
if (-not (Test-Path $YtdlpPath)) {
    Write-Host "Downloading yt-dlp.exe..."
    Invoke-WebRequest -Uri "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" -OutFile $YtdlpPath
}

Write-Host "Running build.py..."
python (Join-Path $Root "scripts\build.py")

$Exe = Join-Path $Root "dist\MediaFetch\MediaFetch.exe"
if (-not (Test-Path $Exe)) {
    Write-Error "Build failed: dist\MediaFetch\MediaFetch.exe not found"
}

if ($Installer) {
    & (Join-Path $Root "scripts\build_installer.ps1")
}

Write-Host "Release folder: $(Split-Path -Parent $Exe)"
Write-Host "Launcher:       $Exe"
