# Download Space Grotesk and Space Mono fonts for offline use

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$FontDir = Join-Path $Root "resources\fonts"
New-Item -ItemType Directory -Force -Path $FontDir | Out-Null

$base = "https://cdn.jsdelivr.net/fontsource/fonts"
$fonts = @{
    "SpaceGrotesk-Regular.ttf"  = "$base/space-grotesk@5.2.8/latin-400-normal.ttf"
    "SpaceGrotesk-Medium.ttf"   = "$base/space-grotesk@5.2.8/latin-500-normal.ttf"
    "SpaceGrotesk-SemiBold.ttf" = "$base/space-grotesk@5.2.8/latin-600-normal.ttf"
    "SpaceGrotesk-Bold.ttf"     = "$base/space-grotesk@5.2.8/latin-700-normal.ttf"
    "SpaceMono-Regular.ttf"     = "$base/space-mono@5.2.8/latin-400-normal.ttf"
    "SpaceMono-Bold.ttf"        = "$base/space-mono@5.2.8/latin-700-normal.ttf"
}

foreach ($entry in $fonts.GetEnumerator()) {
    $dest = Join-Path $FontDir $entry.Key
    if (-not (Test-Path $dest)) {
        Write-Host "Downloading $($entry.Key)..."
        Invoke-WebRequest -Uri $entry.Value -OutFile $dest -UseBasicParsing
    } else {
        Write-Host "Already present: $($entry.Key)"
    }
}

Write-Host "Fonts ready in $FontDir"
