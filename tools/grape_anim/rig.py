"""Cut-out rig for the grape character, built from the parts sheet."""
from PIL import Image
import numpy as np, math, os

PARTS = 'parts'
_cache = {}


def set_parts_dir(path):
    """Point the loader at a different character's cut-outs."""
    global PARTS
    PARTS = path
    _cache.clear()

def part(name):
    """Load a part as premultiplied float RGBA."""
    if name not in _cache:
        im = Image.open(os.path.join(PARTS, f'{name}.png')).convert('RGBA')
        a = np.array(im).astype(np.float32) / 255.0
        a[..., :3] *= a[..., 3:4]          # premultiply
        _cache[name] = a
    return _cache[name]

def _to_img(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA')

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = np.zeros((h, w, 4), np.float32)   # premultiplied

    def draw(self, name, pivot, pos, angle=0.0, sx=1.0, sy=1.0, shade=1.0, alpha=1.0, flip=False):
        src = part(name)
        ph, pw = src.shape[:2]
        px, py = pivot
        if flip:
            src = src[:, ::-1]
            px = pw - px
        tx, ty = pos
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)
        # inverse map: out -> in
        coef = (ca / sx,  sa / sx, px - (tx * ca + ty * sa) / sx,
                -sa / sy, ca / sy, py - (-tx * sa + ty * ca) / sy)
        layer = _to_img(src).transform((self.w, self.h), Image.AFFINE, coef,
                                       resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
        L = np.array(layer).astype(np.float32) / 255.0
        if shade != 1.0:
            L[..., :3] *= shade
        if alpha != 1.0:
            L *= alpha
        self.buf = L + self.buf * (1.0 - L[..., 3:4])

    def ellipse(self, cx, cy, rx, ry, rgb, a):
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        m = np.clip((1.0 - d) * 3.0, 0, 1).astype(np.float32) * a
        L = np.zeros_like(self.buf)
        L[..., 0], L[..., 1], L[..., 2] = rgb
        L[..., :3] *= m[..., None]
        L[..., 3] = m
        self.buf = L + self.buf * (1.0 - L[..., 3:4])

    def image(self):
        out = self.buf.copy()
        a = np.maximum(out[..., 3:4], 1e-6)
        out[..., :3] /= a                       # un-premultiply
        return _to_img(out)
