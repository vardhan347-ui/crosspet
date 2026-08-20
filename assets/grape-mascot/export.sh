#!/usr/bin/env bash
# Renders grape-animation.html into shareable video files.
#   ./export.sh            -> mp4 (white + dark), transparent webm, gif, poster
# Override the encoder with:  FFMPEG=/path/to/ffmpeg ./export.sh
set -euo pipefail
cd "$(dirname "$0")"

FFMPEG="${FFMPEG:-ffmpeg}"
SIZE="${SIZE:-1000}"
FPS="${FPS:-30}"
LOOPS="${LOOPS:-3}"          # how many times the 2.6s cycle repeats in the mp4
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

render() { node render.mjs "$TMP/$1" "$SIZE" "$FPS" "$2"; }

render white white
"$FFMPEG" -y -loglevel error -stream_loop $((LOOPS - 1)) -framerate "$FPS" -i "$TMP/white/f_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -movflags +faststart grape-animation.mp4
cp "$TMP/white/f_0000.png" poster.png

"$FFMPEG" -y -loglevel error -framerate "$FPS" -i "$TMP/white/f_%04d.png" \
  -vf "fps=25,scale=440:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3" \
  -loop 0 grape-animation.gif

render dark dark
"$FFMPEG" -y -loglevel error -stream_loop $((LOOPS - 1)) -framerate "$FPS" -i "$TMP/dark/f_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -movflags +faststart grape-animation-dark.mp4

render alpha none
"$FFMPEG" -y -loglevel error -stream_loop $((LOOPS - 1)) -framerate "$FPS" -i "$TMP/alpha/f_%04d.png" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 -row-mt 1 grape-animation-alpha.webm

ls -lh grape-animation.mp4 grape-animation-dark.mp4 grape-animation.gif grape-animation-alpha.webm poster.png
