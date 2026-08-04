[CmdletBinding()]
param(
    [switch]$KeepStaging
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$DistDir = Join-Path $RepoRoot "dist"
$AddonSourceDir = Join-Path $RepoRoot "addon"
$AddonStageDir = Join-Path $DistDir "blender_mcp_bridge"
$ZipPath = Join-Path $DistDir "blender_mcp_bridge.zip"

$RequiredFiles = @(
    (Join-Path $AddonSourceDir "__init__.py"),
    (Join-Path $AddonSourceDir "models.py")
)

foreach ($File in $RequiredFiles) {
    if (-not (Test-Path -LiteralPath $File -PathType Leaf)) {
        throw "Required add-on file not found: $File"
    }
}

New-Item -ItemType Directory -Path $DistDir -Force | Out-Null

if (Test-Path -LiteralPath $AddonStageDir) {
    Remove-Item -LiteralPath $AddonStageDir -Recurse -Force
}

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

New-Item -ItemType Directory -Path $AddonStageDir -Force | Out-Null

Copy-Item -LiteralPath (Join-Path $AddonSourceDir "__init__.py") `
    -Destination (Join-Path $AddonStageDir "__init__.py") `
    -Force

Copy-Item -LiteralPath (Join-Path $AddonSourceDir "models.py") `
    -Destination (Join-Path $AddonStageDir "models.py") `
    -Force

Compress-Archive `
    -Path $AddonStageDir `
    -DestinationPath $ZipPath `
    -CompressionLevel Optimal `
    -Force

if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
    throw "Add-on ZIP was not created: $ZipPath"
}

$ZipInfo = Get-Item -LiteralPath $ZipPath

Write-Host ""
Write-Host "Blender MCP add-on package created successfully."
Write-Host "ZIP: $($ZipInfo.FullName)"
Write-Host "Size: $($ZipInfo.Length) bytes"
Write-Host ""

if (-not $KeepStaging) {
    Remove-Item -LiteralPath $AddonStageDir -Recurse -Force
    Write-Host "Removed staging folder: $AddonStageDir"
}
else {
    Write-Host "Kept staging folder: $AddonStageDir"
}
