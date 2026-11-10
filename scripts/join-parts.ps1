Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

$parts = Get-ChildItem 'dist-assets/oh6-opi5plus-20261106.img.part*' | Sort-Object Name
if (-not $parts) { throw 'no image parts found' }

$out = [IO.File]::Create((Join-Path (Get-Location) 'update.img'))
try {
    foreach ($p in $parts) {
        $in = [IO.File]::OpenRead($p.FullName)
        try { $in.CopyTo($out) } finally { $in.Dispose() }
        Write-Host ("appended {0} ({1} bytes)" -f $p.Name, $p.Length)
    }
} finally { $out.Dispose() }

Write-Host ("joined: {0} bytes" -f (Get-Item update.img).Length)
$hash = (Get-FileHash update.img -Algorithm SHA256).Hash.ToLower()
Write-Host "sha256: $hash"
Write-Host 'expected: 8994286e12c2b8a05aafd9479026fffafc34112ff47ddc199fe0cf5725f38d34'
