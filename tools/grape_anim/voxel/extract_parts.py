"""Cut the voxel grape's parts sheet into individual transparent PNGs.

The sheet carries an alpha channel, so each piece is a connected component of
the alpha mask. Eye pairs whose two eyes don't touch come out as separate
components and are glued back together at their original spacing.

    python3 extract_parts.py <parts_sheet.png>
"""
import sys, os, json
from collections import deque
import numpy as np
from PIL import Image

# connected-component id (raster-scan order) -> name
NAMES = {
    1: 'body', 2: 'sprig', 3: 'arm_l', 5: 'arm_r', 4: 'leg_a', 6: 'leg_b',
    7: 'eyes_happy',
    8: 'eye_t_l', 10: 'eye_t_r', 9: 'eye_wide_l', 11: 'eye_wide_r',
    14: 'eye_shut_l', 15: 'eye_shut_r', 12: 'eye_t2_l', 13: 'eye_x_r',
    19: 'mouth_open', 22: 'mouth_smirk', 16: 'mouth_tongue', 20: 'mouth_teeth',
    21: 'mouth_small', 23: 'mouth_line', 17: 'mouth_o', 18: 'mouth_wide',
}
PAIRS = {'eyes_t': ('eye_t_l', 'eye_t_r'), 'eyes_wide': ('eye_wide_l', 'eye_wide_r'),
         'eyes_shut': ('eye_shut_l', 'eye_shut_r'), 'eyes_wink': ('eye_t2_l', 'eye_x_r')}

# the walk rig needs the leg split at the ankle; the shin ends in a disc centred
# on the ankle pivot so the (wider) shoe cuff can never uncover its cut end
CUT, ANKLE_X, ANKLE_Y, BALL_R, TUBE_H, SHOE_TOP = 212, 119, 236, 39, 280, 214


def label(mask):
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                n += 1
                lab[y, x] = n
                q = deque([(y, x)])
                while q:
                    cy, cx = q.popleft()
                    for ny, nx in ((cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n
                            q.append((ny, nx))
    return lab, n


def main(src):
    rgba = np.array(Image.open(src).convert('RGBA'))
    lab, n = label(rgba[..., 3] > 60)
    os.makedirs('parts', exist_ok=True)
    meta = {}
    for comp in range(1, n + 1):
        name = NAMES.get(comp)
        if name is None:
            continue
        m = lab == comp
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        out = rgba[y0:y1, x0:x1].copy()
        out[..., 3] *= m[y0:y1, x0:x1]
        Image.fromarray(out).save(f'parts/{name}.png')
        meta[name] = {'sheet_bbox': [int(x0), int(y0), int(x1), int(y1)]}

    for out_name, (a, b) in PAIRS.items():
        ba, bb = meta[a]['sheet_bbox'], meta[b]['sheet_bbox']
        x0, y0 = min(ba[0], bb[0]), min(ba[1], bb[1])
        x1, y1 = max(ba[2], bb[2]), max(ba[3], bb[3])
        canvas = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
        for nm, bx in ((a, ba), (b, bb)):
            canvas.alpha_composite(Image.open(f'parts/{nm}.png'), (bx[0] - x0, bx[1] - y0))
        canvas.save(f'parts/{out_name}.png')
        meta[out_name] = {'sheet_bbox': [int(x0), int(y0), int(x1), int(y1)]}
        os.remove(f'parts/{a}.png')
        os.remove(f'parts/{b}.png')
        meta.pop(a); meta.pop(b)

    leg = np.array(Image.open('parts/leg_a.png').convert('RGBA')).astype(np.float32)
    tube = leg[:TUBE_H].copy()
    yy, xx = np.mgrid[0:TUBE_H, 0:leg.shape[1]]
    tube[..., 3] *= ((yy <= CUT) | ((xx - ANKLE_X) ** 2 + (yy - ANKLE_Y) ** 2 <= BALL_R ** 2))
    tube[..., :3] *= 1 - np.clip((yy - 196) / 22.0, 0, 1)[..., None] * 0.30
    Image.fromarray(np.clip(tube, 0, 255).astype(np.uint8)).save('parts/leg_tube.png')
    Image.fromarray(leg[SHOE_TOP:].astype(np.uint8)).save('parts/leg_shoe.png')

    json.dump(meta, open('parts/parts.json', 'w'), indent=1)
    print(f'wrote {len(meta)} parts + leg_tube/leg_shoe to parts/')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'parts_sheet.png')
