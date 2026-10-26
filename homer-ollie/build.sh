#!/usr/bin/env bash
# Genera homer-ollie.mp4 (1080p60 con sonido), homer-ollie.gif y ollie-sfx.m4a.
set -euo pipefail
cd "$(dirname "$0")"

node record.js 60
python3 sfx.py build/timeline.json build/sfx.wav

ffmpeg -loglevel error -y -i build/sfx.wav -c:a aac -b:a 160k ollie-sfx.m4a
ffmpeg -loglevel error -y -i build/video.mp4 -i build/sfx.wav \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart homer-ollie.mp4
ffmpeg -loglevel error -y -i build/video.mp4 \
  -vf "fps=20,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
  -loop 0 homer-ollie.gif

echo "Listo: homer-ollie.mp4, homer-ollie.gif, ollie-sfx.m4a"
