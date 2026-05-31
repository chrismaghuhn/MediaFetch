# Download FFmpeg for local development (required by yt-dlp for video merges)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BinDir = Join-Path $Root "resources\bin"
$FfmpegPath = Join-Path $BinDir "ffmpeg.exe"

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

if (Test-Path $FfmpegPath) {
    Write-Host "FFmpeg already present: $FfmpegPath"
    exit 0
}

Write-Host "Downloading FFmpeg..."
$FfmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$TempZip = Join-Path $env:TEMP "ffmpeg-dev.zip"
$TempExtract = Join-Path $env:TEMP "ffmpeg_dev_extract"

Invoke-WebRequest -Uri $FfmpegUrl -OutFile $TempZip
Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
$FfmpegSrc = Get-ChildItem -Path $TempExtract -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
Copy-Item $FfmpegSrc.FullName -Destination $FfmpegPath

Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Done. FFmpeg installed to $FfmpegPath"
