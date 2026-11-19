#!/bin/bash
# DA 릴스 스킬 처음 설치 점검 (맥 전용). 여러 번 실행해도 안전.
set -e
ok() { echo "✅ $1"; }
no() { echo "❌ $1"; }
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then ok "ffmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3)"
else
  if command -v brew >/dev/null; then echo "ffmpeg 설치 중 (몇 분 걸려요)…"; brew install ffmpeg && ok "ffmpeg 설치됨"
  else no "ffmpeg 없음 → 터미널에서 Homebrew(https://brew.sh) 설치 후 'brew install ffmpeg'"; fi
fi
mkdir -p ~/.da-reels
if [ ! -x ~/.da-reels/venv/bin/python ]; then
  python3 -m venv ~/.da-reels/venv && ~/.da-reels/venv/bin/pip -q install --upgrade pip >/dev/null 2>&1 || true
fi
~/.da-reels/venv/bin/pip -q install pillow >/dev/null 2>&1 && ok "파이썬 도구(Pillow)"
K="$(dirname "$0")/../keys"
if [ -s "$K/pixabay_key" ] || [ -s ~/.da-reels/pixabay_key ]; then ok "Pixabay 키 (크롬 없을 때 영상 검색용)"
else echo "ℹ️ Pixabay 키 없음 — 클로드 크롬으로 Pexels 검색하면 필요 없음"; fi
