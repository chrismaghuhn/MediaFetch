# MediaFetch release build script for Windows
# Downloads FFmpeg, runs PyInstaller, creates ZIP for GitHub Releases

param(
    [switch]$SkipFfmpeg
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BinDir = Join-Path $Root "resources\bin"
$DistDir = Join-Path $Root "dist\MediaFetch"

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
        Write-Host "FFmpeg saved to $FfmpegPath"
    }
}

$YtdlpPath = Join-Path $BinDir "yt-dlp.exe"
if (-not (Test-Path $YtdlpPath)) {
    Write-Host "Downloading yt-dlp.exe..."
    $YtdlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    Invoke-WebRequest -Uri $YtdlpUrl -OutFile $YtdlpPath
    Write-Host "yt-dlp saved to $YtdlpPath"
}

Write-Host "Running PyInstaller..."
Push-Location $Root
try {
    python -m PyInstaller build\mediafetch.spec --noconfirm
} finally {
    Pop-Location
}

if (-not (Test-Path $DistDir)) {
    Write-Error "Build failed: dist\MediaFetch not found"
}

# Copy binaries into dist
Copy-Item $BinDir\ffmpeg.exe -Destination (Join-Path $DistDir "bin") -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $DistDir "bin") | Out-Null
Copy-Item $BinDir\ffmpeg.exe -Destination (Join-Path $DistDir "bin\ffmpeg.exe") -Force
Copy-Item $BinDir\yt-dlp.exe -Destination (Join-Path $DistDir "bin\yt-dlp.exe") -Force

$ZipPath = Join-Path $Root "dist\MediaFetch-win64.zip"
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path $DistDir -DestinationPath $ZipPath
Write-Host "Release ZIP: $ZipPath"
