"""Small, embeddable copies of the animation + the parts it is built from."""
import os, base64, json
from PIL import Image

os.makedirs('out/web', exist_ok=True)
N, PH = 24, 360                                   # preview frame height

frames = [Image.open(f'out/frames/walk_{i:02d}.png') for i in range(N)]
w0, h0 = frames[0].size
pw = round(w0 * PH / h0)
strip = Image.new('RGBA', (pw * N, PH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    strip.paste(f.resize((pw, PH), Image.LANCZOS), (i * pw, 0))
strip.save('out/web/strip_small.png', optimize=True)

RIG = ['body', 'leg_tube', 'leg_shoe', 'arm_hang', 'vine', 'leaf',
       'eyes_happy', 'eyes_closed', 'mouth_open_big']
for n in RIG:
    im = Image.open(f'parts/{n}.png')
    im.thumbnail((190, 190), Image.LANCZOS)
    im.save(f'out/web/part_{n}.png', optimize=True)

meta = {'frames': N, 'frameW': pw, 'frameH': PH}
json.dump(meta, open('out/web/meta.json', 'w'))
for f in sorted(os.listdir('out/web')):
    print(f'{f:26s} {os.path.getsize("out/web/"+f)/1024:7.1f} KB')
print(meta)
