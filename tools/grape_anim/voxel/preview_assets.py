"""Small, embeddable copies of the swagger walk + the parts it is built from."""
import os, json
from PIL import Image

os.makedirs('out/web', exist_ok=True)
PH = 260
frames = [Image.open(f'out/frames/swagger_{i:02d}.png') for i in range(53)]
w0, h0 = frames[0].size
pw = round(w0 * PH / h0)
strip = Image.new('RGBA', (pw * len(frames), PH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    strip.paste(f.resize((pw, PH), Image.LANCZOS), (i * pw, 0))
strip.save('out/web/strip_small.png', optimize=True)
# webp keeps alpha and is ~10x smaller as a data: URI
strip.save('out/web/strip_small.webp', quality=90, method=6)

for n in ('body', 'leg_tube', 'leg_shoe', 'arm_l', 'arm_r', 'sprig',
          'eyes_happy', 'eyes_wide', 'mouth_open'):
    im = Image.open(f'parts/{n}.png')
    im.thumbnail((180, 180), Image.LANCZOS)
    im.save(f'out/web/part_{n}.png', optimize=True)

json.dump({'frames': len(frames), 'frameW': pw, 'frameH': PH},
          open('out/web/meta.json', 'w'))
for f in sorted(os.listdir('out/web')):
    print(f'{f:26s} {os.path.getsize("out/web/"+f)/1024:7.1f} KB')
