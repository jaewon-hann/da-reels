# DA 릴스 스킬 설치 점검 (윈도우). 여러 번 실행해도 안전.
# 실행: powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Continue"
function ok($m) { Write-Host "✅ $m" }
function no($m) { Write-Host "❌ $m" }

# 1. ffmpeg
if ((Get-Command ffmpeg -ErrorAction SilentlyContinue) -and (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
  ok "ffmpeg"
} elseif (Get-Command winget -ErrorAction SilentlyContinue) {
  Write-Host "ffmpeg 설치 중 (몇 분 걸려요)…"
  winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements | Out-Null
  no "ffmpeg 설치 완료 — Claude Code(터미널)를 껐다 켜야 인식돼요"
} else {
  no "ffmpeg 없음 → https://www.gyan.dev/ffmpeg/builds/ 에서 받아 PATH 에 추가"
}

# 2. 파이썬 + Pillow (전용 가상환경)
$py = $null
foreach ($c in @("py", "python", "python3")) { if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break } }
if (-not $py) {
  no "파이썬 없음 → 'winget install Python.Python.3.12' 후 다시 실행"
} else {
  $venv = Join-Path $env:USERPROFILE ".da-reels\venv"
  if (-not (Test-Path "$venv\Scripts\python.exe")) {
    if ($py -eq "py") { & py -3 -m venv $venv } else { & $py -m venv $venv }
  }
  & "$venv\Scripts\python.exe" -m pip -q install pillow 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { ok "파이썬 도구(Pillow) — $venv\Scripts\python.exe" } else { no "Pillow 설치 실패" }
}

# 3. 영상 검색 키 (선택)
$k1 = Join-Path $PSScriptRoot "..\keys\pixabay_key"
$k2 = Join-Path $env:USERPROFILE ".da-reels\pixabay_key"
if ((Test-Path $k1) -or (Test-Path $k2)) { ok "Pixabay 키 (크롬 없을 때 영상 검색용)" }
else { Write-Host "ℹ️ Pixabay 키 없음 — 클로드 크롬으로 Pexels 검색하면 필요 없음" }
