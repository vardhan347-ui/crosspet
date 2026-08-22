"""Cut the grape character's parts sheet into individual transparent PNGs.

The sheet already carries an alpha channel, so each part is just a connected
component of the alpha mask. Run once; `parts/` is checked in, so this is only
needed if the source sheet changes.

    python3 extract_parts.py <parts_sheet.png>
"""
import sys, os, json
from collections import deque
import numpy as np
from PIL import Image

# connected-component id (raster-scan order over the sheet) -> name
NAMES = {
    1: 'vine', 2: 'leaf', 3: 'body', 4: 'eyes_squint_x', 5: 'eyes_wide',
    6: 'eyes_happy', 7: 'eyes_happy_alt', 8: 'eyes_wink_x', 9: 'eyes_closed',
    10: 'eyes_sleepy', 11: 'arm_point', 12: 'eyes_angry', 13: 'arm_hang',
    14: 'mouth_small_o', 15: 'mouth_open_big', 16: 'mouth_smile_thin',
    17: 'arm_openhand', 18: 'arm_bent_fist', 19: 'mouth_grin_teeth',
    20: 'mouth_smile_thick', 21: 'mouth_tongue_l', 22: 'leg_a', 23: 'leg_b',
    24: 'mouth_open_tongue', 25: 'mouth_open_white', 26: 'hand_open',
    27: 'mouth_line', 28: 'fist', 29: 'mouth_tongue_r', 30: 'leg_bent_side',
    31: 'leg_bent', 32: 'mouth_frown', 33: 'mouth_smile_small', 34: 'shoe',
    35: 'mouth_tiny', 36: 'mouth_smile', 37: 'mouth_open_small',
}

# the walk rig needs a leg split at the ankle; the tube ends in a disc centred
# on the ankle pivot so the (oversized) shoe cuff can never uncover its cut end
CUT, ANKLE_X, ANKLE_Y, BALL_R, TUBE_H = 160, 58, 182, 35, 219
SHOE_TOP = 164


def label(mask):
    """4-connected components, returned as an int32 label image."""
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
    im = Image.open(src).convert('RGBA')
    rgba = np.array(im)
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
    json.dump(meta, open('parts/parts.json', 'w'), indent=1)

    # --- derived rig parts ---------------------------------------------
    leg = np.array(Image.open('parts/leg_a.png').convert('RGBA')).astype(np.float32)
    tube = leg[:TUBE_H].copy()
    yy, xx = np.mgrid[0:TUBE_H, 0:leg.shape[1]]
    ball = (xx - ANKLE_X) ** 2 + (yy - ANKLE_Y) ** 2 <= BALL_R ** 2
    tube[..., 3] *= ((yy <= CUT) | ball)
    tube[..., :3] *= 1 - np.clip((yy - 146) / 22.0, 0, 1)[..., None] * 0.34
    Image.fromarray(np.clip(tube, 0, 255).astype(np.uint8)).save('parts/leg_tube.png')
    Image.fromarray(leg[SHOE_TOP:].astype(np.uint8)).save('parts/leg_shoe.png')

    print(f'wrote {len(meta)} parts + leg_tube/leg_shoe to parts/')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'parts_sheet.png')
