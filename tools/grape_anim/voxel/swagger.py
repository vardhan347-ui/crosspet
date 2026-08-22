"""Voxel grape walking the reference Lottie's swagger.

Timing and performance come straight from `ref_curves.json` — the per-frame
values read off the "Bud Leaf 2" After Effects rig: 53 frames at 30fps, one
stride, a double bounce (four bobs), a slow lean that peaks mid-loop, a single
arm sweep, a drifting head, and an expression change on frames 22-29.

The reference animates its legs by morphing a noodle outline. Rigid voxel
shins can't morph, so the legs are re-solved as one-bone IK against the same
stride length, stance/swing split, contact phasing and depth offsets.

Part scales are per-part: the parts sheet lays each piece out at whatever size
suited the layout, so body, legs, arms, sprig and face are each scaled to the
proportions measured off the hero render.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rig
from rig import Canvas

HERE = os.path.dirname(os.path.abspath(__file__))
rig.set_parts_dir(os.path.join(HERE, 'parts'))
CURVES = json.load(open(os.path.join(HERE, 'ref_curves.json')))
N_FRAMES, FPS = len(CURVES), 30

# ---- per-part scale, measured against the hero render -----------------
BODY_S, LEG_S, ARM_S, SPRIG_S, EYES_S, MOUTH_S = 1.34, 1.05, 0.92, 1.12, 1.02, 0.98

# ---- part pivots ------------------------------------------------------
TUBE_HIP   = (111, 6)
TUBE_ANKLE = (119, 236)
TUBE_LEN   = (TUBE_ANKLE[1] - TUBE_HIP[1]) * LEG_S
SHOE_ANKLE = (119, 22)
SHOE_SX, SHOE_SY = 1.06 * LEG_S, 1.03 * LEG_S
SHOE_DROP  = (157 - SHOE_ANKLE[1]) * SHOE_SY
ARM_SHO    = (85, 10)
SPRIG_BASE = (45, 225)
EYES_PIV, MOUTH_PIV = (122, 82), (88, 51)

# ---- body-local anchors (body.png is 450 x 494) -----------------------
BODY_ORIGIN = (225, 440)
HIP_N, HIP_F = (268, 470), (172, 470)
SHO_N, SHO_F = (425, 322), (30, 292)
EYES, MOUTH  = (181, 258), (188, 372)
SPRIG_A      = (258, 116)

# ---- staging ----------------------------------------------------------
W, H     = 1400, 1520
CENTER_X = 700
SOLE_Y   = 1345.0
ANKLE_Y  = SOLE_Y - SHOE_DROP
HIP_Y    = ANKLE_Y - TUBE_LEN

# ---- reference -> this character --------------------------------------
S = (TUBE_LEN + SHOE_DROP) / 248.0        # ref hip->ground is 248 px

# the reference's noodle legs reach a 255px stride by curving through an S; a
# rigid shin at that reach just reads as the splits, so it is pulled back to 58%
STRIDE   = 255.0 * S * 0.58
LIFT     = 62.0 * S * 0.80
STANCE   = 24.0 / N_FRAMES
NEAR_DX  = 103.0 * S * 0.40               # near foot sits right of and below
NEAR_DY  = 20.0 * S * 1.30                       # the far one, for depth
CONTACT_N, CONTACT_F = 0.0, 26.0

ARM_UP     = 142.0
ARM_OUT    = -14.0    # the hanging arm sits a little clear of the body    # turns the hanging arm asset into a raised one
SWEEP_GAIN = 0.50     # the reference sweeps 103 degrees; a rigid arm needs less
HEAD_GAIN  = 0.45
SHADE_FAR  = 0.72
WIDE_EYES  = range(22, 30)

BODY_SX = BODY_SY = 1.0


def foot(phase):
    """Ankle (fore/aft, lift) for a leg `phase` in [0,1) since its own contact."""
    p = phase % 1.0
    if p < STANCE:
        return -STRIDE / 2 + STRIDE * (p / STANCE), 0.0
    t = (p - STANCE) / (1 - STANCE)
    e = t * t * (3 - 2 * t)
    return STRIDE / 2 - STRIDE * e, LIFT * math.sin(math.pi * t) ** 0.8


def foot_roll(phase):
    p = phase % 1.0
    if p < 0.09:          return -15 * (1 - p / 0.09)
    if p < STANCE * 0.7:  return 0.0
    if p < STANCE:        return 24 * ((p - STANCE * 0.7) / (STANCE * 0.3))
    t = (p - STANCE) / (1 - STANCE)
    return 24 * (1 - min(1.0, t / 0.5)) - 15 * max(0.0, (t - 0.75) / 0.25)


def local_to_world(pt, bpos, bang):
    a = math.radians(bang)
    ux = (pt[0] - BODY_ORIGIN[0]) * BODY_SX * BODY_S
    uy = (pt[1] - BODY_ORIGIN[1]) * BODY_SY * BODY_S
    return (bpos[0] + ux * math.cos(a) - uy * math.sin(a),
            bpos[1] + ux * math.sin(a) + uy * math.cos(a))


def draw_leg(c, phase, hip_local, bpos, bang, far):
    hx, hy = local_to_world(hip_local, bpos, bang)
    fore, lift = foot(phase)
    fx = CENTER_X + fore + (0.0 if far else NEAR_DX)
    fy = ANKLE_Y - lift - (NEAR_DY if far else 0.0)
    dx, dy = fx - hx, fy - hy
    stretch = min(1.26, max(0.58, math.hypot(dx, dy) / TUBE_LEN))
    ang = math.degrees(math.atan2(dx, dy))
    sh = SHADE_FAR if far else 1.0
    c.draw('leg_tube', TUBE_HIP, (hx, hy), angle=ang,
           sx=LEG_S / (1 + (stretch - 1) * 0.22), sy=stretch * LEG_S, shade=sh)
    ax = hx + math.sin(math.radians(ang)) * TUBE_LEN * stretch
    ay = hy + math.cos(math.radians(ang)) * TUBE_LEN * stretch
    c.draw('leg_shoe', SHOE_ANKLE, (ax, ay),
           angle=ang * 0.55 + foot_roll(phase) * 0.85,
           sx=SHOE_SX, sy=SHOE_SY, shade=sh)


def frame(i):
    global BODY_SX, BODY_SY
    k = CURVES[i % N_FRAMES]
    bang = k['brot']
    squash = -k['bdy'] / 60.0 * 0.045
    BODY_SX, BODY_SY = 1 + squash * 0.7, 1 - squash
    bpos = (CENTER_X + k['bdx'] * S, HIP_Y + k['bdy'] * S)

    c = Canvas(W, H)
    phN, phF = (i - CONTACT_N) / N_FRAMES, (i - CONTACT_F) / N_FRAMES
    for ph, dx, dy in ((phF, 0.0, -NEAR_DY), (phN, NEAR_DX, 0.0)):
        fore, lift = foot(ph)
        g = 1 - min(1.0, lift / LIFT)
        c.ellipse(CENTER_X + fore + dx, SOLE_Y + dy + 30,
                  135 * (0.55 + 0.45 * g), 26 * (0.5 + 0.5 * g),
                  (0.10, 0.02, 0.14), 0.24 * g + 0.04)

    # far side — the arm the reference holds up, and the far leg
    c.draw('arm_l', ARM_SHO, local_to_world(SHO_F, bpos, bang),
           angle=ARM_UP + k['hold'] * 0.6, sx=ARM_S * 1.08, sy=ARM_S * 1.08,
           shade=SHADE_FAR)
    draw_leg(c, phF, HIP_F, bpos, bang, far=True)

    c.draw('sprig', SPRIG_BASE, local_to_world(SPRIG_A, bpos, bang),
           angle=bang + k['sdx'] * 0.30, sx=SPRIG_S, sy=SPRIG_S)
    c.draw('body', BODY_ORIGIN, bpos, angle=bang,
           sx=BODY_SX * BODY_S, sy=BODY_SY * BODY_S)

    hx = k['hdx'] * S * HEAD_GAIN / BODY_S
    hy = (k['hdy'] - 26.0) * S * HEAD_GAIN / BODY_S
    wide = (i % N_FRAMES) in WIDE_EYES
    c.draw('eyes_wide' if wide else 'eyes_happy', EYES_PIV,
           local_to_world((EYES[0] + hx, EYES[1] + hy), bpos, bang),
           angle=bang, sx=EYES_S, sy=EYES_S)
    c.draw('mouth_open', MOUTH_PIV,
           local_to_world((MOUTH[0] + hx, MOUTH[1] + hy), bpos, bang),
           angle=bang, sx=MOUTH_S, sy=MOUTH_S)

    # near side — the sweeping arm rides in front of the body
    c.draw('arm_r', ARM_SHO, local_to_world(SHO_N, bpos, bang),
           angle=ARM_OUT + k['sweep'] * SWEEP_GAIN, sx=ARM_S, sy=ARM_S)
    draw_leg(c, phN, HIP_N, bpos, bang, far=False)
    return c.image()


if __name__ == '__main__':
    from PIL import Image
    idx = list(range(0, 53, 6))
    ims = [frame(i) for i in idx]
    cols = 3
    rows = (len(ims) + cols - 1) // cols
    sc = 3
    s = Image.new('RGB', (cols * W // sc, rows * H // sc), (250, 248, 252))
    for i, im in enumerate(ims):
        b = Image.new('RGB', im.size, (250, 248, 252)); b.paste(im, (0, 0), im)
        s.paste(b.resize((W // sc, H // sc), Image.LANCZOS),
                ((i % cols) * W // sc, (i // cols) * H // sc))
    s.save('check.png'); print(idx)
