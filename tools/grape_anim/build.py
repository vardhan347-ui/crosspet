"""Render the grape walk cycle to GIF / animated WebP / sprite sheet / PNG frames."""
import os, math
import numpy as np
from PIL import Image
import walk

FPS      = 12
PER_STEP = 12                    # frames per stride
STRIDES  = 2                     # two strides so the blink can live in the loop
N        = PER_STEP * STRIDES
BLINK    = {16, 17}              # frames where the eyes close
OUT      = 'out'
TARGET_H = 520                   # final frame height
MATTE    = (247, 244, 250)

os.makedirs(f'{OUT}/frames', exist_ok=True)

print(f'rendering {N} frames...')
raw = [walk.frame((i % PER_STEP) / PER_STEP, blink=1.0 if i in BLINK else 0.0) for i in range(N)]

# common crop across every frame so nothing jitters
box = None
for im in raw:
    b = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                 max(box[2], b[2]), max(box[3], b[3]))
M = 14
box = (box[0] - M, box[1] - M, box[2] + M, box[3] + M)
scale = TARGET_H / (box[3] - box[1])
size = (int(round((box[2] - box[0]) * scale)), TARGET_H)
print('crop', box, '-> frame', size)

frames = [im.crop(box).resize(size, Image.LANCZOS) for im in raw]
for i, f in enumerate(frames):
    f.save(f'{OUT}/frames/walk_{i:02d}.png')

# sprite sheet (transparent), 8 columns
COLS = 8
rows = (N + COLS - 1) // COLS
sheet = Image.new('RGBA', (COLS * size[0], rows * size[1]), (0, 0, 0, 0))
for i, f in enumerate(frames):
    sheet.paste(f, ((i % COLS) * size[0], (i // COLS) * size[1]))
sheet.save(f'{OUT}/grape_walk_sheet.png')

# single-row strip, handy for CSS steps() playback
strip = Image.new('RGBA', (N * size[0], size[1]), (0, 0, 0, 0))
for i, f in enumerate(frames):
    strip.paste(f, (i * size[0], 0))
strip.save(f'{OUT}/grape_walk_strip.png')

# animated WebP keeps real alpha
frames[0].save(f'{OUT}/grape_walk.webp', save_all=True, append_images=frames[1:],
               duration=int(1000 / FPS), loop=0, quality=92, method=6)

# GIF: matte onto a light background (GIF alpha is 1-bit and fringes badly)
gif = []
for f in frames:
    bg = Image.new('RGBA', f.size, MATTE + (255,))
    bg.alpha_composite(f)
    gif.append(bg.convert('RGB').quantize(colors=128, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
gif[0].save(f'{OUT}/grape_walk.gif', save_all=True, append_images=gif[1:],
            duration=int(1000 / FPS), loop=0, optimize=True)

for f in sorted(os.listdir(OUT)):
    p = f'{OUT}/{f}'
    if os.path.isfile(p):
        print(f'{f:26s} {os.path.getsize(p)/1024:8.1f} KB')
