# Publish this repository to GitHub and upload the release assets.
# Usage (from the repository root):
#   powershell -ExecutionPolicy Bypass -File .\scripts\publish.ps1
# Optional:
#   -Repo my-repo-name  -Tag v1.0.0-base  -Proxy http://127.0.0.1:7897
param(
    [string]$Repo = 'oh6-opi5plus-image',
    [string]$Tag = 'v1.0.0-base',
    [string]$Proxy = 'http://127.0.0.1:7897'
)

$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

$gh = if (Test-Path '.tools/bin/gh.exe') { (Resolve-Path '.tools/bin/gh.exe').Path } else { 'gh' }
if ($Proxy) {
    $env:HTTPS_PROXY = $Proxy
    $env:HTTP_PROXY = $Proxy
}

& $gh auth status 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GitHub login required: open the URL, enter the one-time code, then return here.'
    & $gh auth login --hostname github.com --git-protocol https --web --skip-ssh-key
    if ($LASTEXITCODE -ne 0) { throw 'GitHub login failed' }
}

$login = (& $gh api user --jq .login).Trim()
$name = (& $gh api user --jq '.name // .login').Trim()
$id = (& $gh api user --jq .id).Trim()
$mail = (& $gh api user --jq '.email // empty').Trim()
if (-not $mail) { $mail = "$id+$login@users.noreply.github.com" }

git config user.name $name
git config user.email $mail
if ($Proxy) { git config 'http.https://github.com.proxy' $Proxy }

if (git status --porcelain) {
    git add -A
    git commit -m 'OpenHarmony 6.0 RK3588 image and board patches'
}

& $gh repo view "$login/$Repo" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $gh repo create $Repo --public --source . --remote origin --push `
        --description 'OpenHarmony 6.0 (RK3588 / Orange Pi 5 Plus) image with verified portrait and ArkWeb patches'
} else {
    git remote get-url origin 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { git remote add origin "https://github.com/$login/$Repo.git" }
    git push -u origin main
}

& $gh release view $Tag 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    $assets = Get-ChildItem dist-assets -File | ForEach-Object { $_.FullName }
    & $gh release create $Tag $assets --title 'v1.0.0-base' --notes-file RELEASE_NOTES.md
    if ($LASTEXITCODE -ne 0) { throw 'release upload failed; rerun to resume with: gh release upload ' + $Tag + ' <file>' }
}

Write-Host ''
Write-Host "repository: https://github.com/$login/$Repo"
Write-Host "release:    https://github.com/$login/$Repo/releases/tag/$Tag"
