"""Render the voxel swagger walk to GIF / animated WebP / sprite sheet / frames."""
import os
from PIL import Image
import swagger

FPS = swagger.FPS            # 30
N   = swagger.N_FRAMES       # 53
OUT = 'out'
TARGET_H = 500
SHEET_H  = 300          # the sheet is the reuse asset; the gif/webp carry full size
MATTE = (247, 244, 250)

os.makedirs(f'{OUT}/frames', exist_ok=True)
print(f'rendering {N} frames...')
raw = [swagger.frame(i) for i in range(N)]

box = None
for im in raw:
    b = im.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox()
    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                 max(box[2], b[2]), max(box[3], b[3]))
M = 16
box = (box[0] - M, box[1] - M, box[2] + M, box[3] + M)
scale = TARGET_H / (box[3] - box[1])
size = (int(round((box[2] - box[0]) * scale)), TARGET_H)
print('crop', box, '-> frame', size)

frames = [im.crop(box).resize(size, Image.LANCZOS) for im in raw]
for i, f in enumerate(frames):
    f.save(f'{OUT}/frames/swagger_{i:02d}.png')

COLS = 8
rows = (N + COLS - 1) // COLS
sw = int(round(size[0] * SHEET_H / size[1]))
small = [f.resize((sw, SHEET_H), Image.LANCZOS) for f in frames]
sheet = Image.new('RGBA', (COLS * sw, rows * SHEET_H), (0, 0, 0, 0))
for i, f in enumerate(small):
    sheet.paste(f, ((i % COLS) * sw, (i // COLS) * SHEET_H))
sheet.save(f'{OUT}/grape_swagger_sheet.png', optimize=True)

strip = Image.new('RGBA', (N * sw, SHEET_H), (0, 0, 0, 0))
for i, f in enumerate(small):
    strip.paste(f, (i * sw, 0))
strip.save(f'{OUT}/grape_swagger_strip.png', optimize=True)
print(f'sheet cel {sw}x{SHEET_H}')

frames[0].save(f'{OUT}/grape_swagger.webp', save_all=True, append_images=frames[1:],
               duration=int(round(1000 / FPS)), loop=0, quality=92, method=4)

gif = []
for f in frames:
    bg = Image.new('RGBA', f.size, MATTE + (255,))
    bg.alpha_composite(f)
    # voxel art is flat-shaded; dithering only adds noise and bytes
    gif.append(bg.convert('RGB').quantize(colors=160, method=Image.MEDIANCUT,
                                          dither=Image.NONE))
gif[0].save(f'{OUT}/grape_swagger.gif', save_all=True, append_images=gif[1:],
            duration=int(round(1000 / FPS)), loop=0, optimize=True)

for f in sorted(os.listdir(OUT)):
    p = f'{OUT}/{f}'
    if os.path.isfile(p):
        print(f'{f:28s} {os.path.getsize(p)/1024:8.1f} KB')
