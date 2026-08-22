"""Grape walk cycle — 1-bone IK legs, counter-swinging arms, secondary vine/leaf.

Everything is assembled from cut-outs of the character parts sheet; see rig.py
for the affine/premultiplied-alpha compositor.
"""
import math
from rig import Canvas

# ---- part pivots (pixel coords inside each part PNG) -------------------
TUBE_HIP    = (45, 8)         # top of the leg tube
TUBE_ANKLE  = (58, 182)       # ankle, inside the shoe cuff
TUBE_LEN    = TUBE_ANKLE[1] - TUBE_HIP[1]      # 174 px at scale 1
SHOE_ANKLE  = (58, 18)        # same ankle point in the shoe crop
SHOE_SX, SHOE_SY = 1.16, 1.05                  # shoe cuff slightly oversized
SHOE_DROP   = (109 - SHOE_ANKLE[1]) * SHOE_SY  # ankle -> sole
ARM_SHO     = (152, 8)

# ---- body-local anchors (body.png is 466 x 527) -----------------------
BODY_ORIGIN = (233, 452)      # body pivot, on the hip line
HIP_N   = (270, 448)          # near (screen-right) hip
HIP_F   = (194, 442)          # far  (screen-left)  hip
SHO_N   = (418, 300)
SHO_F   = ( 50, 300)
EYES    = (238, 230)
MOUTH   = (244, 366)
VINE_A  = (330,  40)
LEAF_A  = (352,  92)

# ---- staging ----------------------------------------------------------
W, H       = 940, 1050
CENTER_X   = 470
SOLE_Y     = 1000.0                    # where the shoes touch the ground
ANKLE_Y    = SOLE_Y - SHOE_DROP        # ankle height at rest
HIP_Y      = ANKLE_Y - TUBE_LEN        # hips with the legs at natural length

STRIDE  = 92.0      # how far each foot travels fore/aft of centre
LIFT    = 50.0      # peak ankle lift during the swing
BOB     = 13.0      # body rise/fall, twice per stride
LEAN    = 2.0       # constant forward lean (walking to the right)
FOOT_N  =  26.0     # lateral offset of the near foot
FOOT_F  = -34.0     # ... and the far one, for depth separation

SHADE_FAR = 0.72

BODY_SX = BODY_SY = 1.0


def foot_path(p):
    """Ankle offset (fore/aft, lift) for cycle phase p.
    p in [0, 0.5) = stance, foot planted and sliding back; [0.5, 1) = swing."""
    p %= 1.0
    if p < 0.5:
        return STRIDE * (1 - 4 * p), 0.0
    t = (p - 0.5) / 0.5
    e = t * t * (3 - 2 * t)                          # smoothstep
    return -STRIDE + 2 * STRIDE * e, LIFT * math.sin(math.pi * t) ** 0.85


def foot_angle(p):
    """Shoe roll: toe up at heel strike, toe down through push-off."""
    p %= 1.0
    if p < 0.12: return -14 * (1 - p / 0.12)
    if p < 0.34: return 0.0
    if p < 0.50: return 24 * ((p - 0.34) / 0.16)
    if p < 0.78: return 24 * (1 - (p - 0.5) / 0.28)
    return -14 * ((p - 0.78) / 0.22)


def local_to_world(pt, body_pos, body_ang):
    """Body-local (body.png px) -> canvas, through the body's own transform."""
    a = math.radians(body_ang)
    ux = (pt[0] - BODY_ORIGIN[0]) * BODY_SX
    uy = (pt[1] - BODY_ORIGIN[1]) * BODY_SY
    return (body_pos[0] + ux * math.cos(a) - uy * math.sin(a),
            body_pos[1] + ux * math.sin(a) + uy * math.cos(a))


def draw_leg(c, p, hip_local, body_pos, body_ang, far):
    hx, hy = local_to_world(hip_local, body_pos, body_ang)
    fore, lift = foot_path(p)
    fx = CENTER_X + fore + (FOOT_F if far else FOOT_N)
    fy = ANKLE_Y - lift
    dx, dy = fx - hx, fy - hy
    stretch = min(1.30, max(0.55, math.hypot(dx, dy) / TUBE_LEN))
    ang = math.degrees(math.atan2(dx, dy))           # 0 = straight down
    sh = SHADE_FAR if far else 1.0
    # rubber-hose volume: the tube narrows a touch as it stretches
    c.draw('leg_tube', TUBE_HIP, (hx, hy), angle=ang,
           sx=1.0 / (1 + (stretch - 1) * 0.25), sy=stretch, shade=sh)
    ax = hx + math.sin(math.radians(ang)) * TUBE_LEN * stretch
    ay = hy + math.cos(math.radians(ang)) * TUBE_LEN * stretch
    # the oversized cuff keeps the tube's cut end covered as the foot rolls
    c.draw('leg_shoe', SHOE_ANKLE, (ax, ay), angle=ang * 0.6 + foot_angle(p) * 0.8,
           sx=SHOE_SX, sy=SHOE_SY, shade=sh)


def draw_arm(c, p, sho_local, body_pos, body_ang, far):
    sx_, sy_ = local_to_world(sho_local, body_pos, body_ang)
    # +angle swings the hand backwards on both sides; each arm opposes its own leg
    ang = 22 * math.cos(2 * math.pi * (p - 0.05)) + 4 * math.sin(2 * math.pi * (p - 0.22))
    c.draw('arm_hang', ARM_SHO, (sx_, sy_), angle=ang, sx=1.1,
           sy=1.1 * (1 + 0.05 * math.cos(2 * math.pi * p)),
           shade=SHADE_FAR if far else 1.0, flip=not far)


def frame(p, blink=0.0):
    """Render one frame. p is the near leg's phase in [0, 1)."""
    global BODY_SX, BODY_SY
    p %= 1.0
    bob    = BOB * math.cos(4 * math.pi * p)          # lowest at contact
    squash = 0.028 * math.cos(4 * math.pi * p)
    BODY_SX, BODY_SY = 1 + squash * 0.8, 1 - squash
    bpos = (CENTER_X + 5 * math.sin(2 * math.pi * p), HIP_Y + bob)
    bang = 2.6 * math.sin(2 * math.pi * p) + LEAN

    c = Canvas(W, H)
    for ph in (p + 0.5, p):                            # contact shadows
        fore, lift = foot_path(ph)
        k = 1 - min(1.0, lift / LIFT)
        c.ellipse(CENTER_X + fore, SOLE_Y + 8, 92 * (0.55 + 0.45 * k),
                  20 * (0.5 + 0.5 * k), (0.12, 0.03, 0.16), 0.26 * k + 0.05)

    draw_leg(c, p + 0.5, HIP_F, bpos, bang, far=True)
    draw_arm(c, p + 0.5, SHO_F, bpos, bang, far=True)

    lag = -4.0 * math.cos(2 * math.pi * (p - 0.18))    # vine/leaf drag
    c.draw('vine', (150, 168), local_to_world(VINE_A, bpos, bang), angle=lag * 1.5)
    c.draw('leaf', (10, 96), local_to_world(LEAF_A, bpos, bang), angle=lag * 2.4,
           sy=1 + 0.03 * math.sin(2 * math.pi * (p - 0.3)))

    c.draw('body', BODY_ORIGIN, bpos, angle=bang, sx=BODY_SX, sy=BODY_SY)

    epos = local_to_world(EYES, bpos, bang)
    ES = 1.8
    if blink > 0.5:
        c.draw('eyes_closed', (60, 46), epos, angle=bang, sx=ES, sy=ES * 0.55)
    else:
        c.draw('eyes_happy', (57, 46), epos, angle=bang, sx=ES, sy=ES)
    c.draw('mouth_open_big', (72, 44), local_to_world(MOUTH, bpos, bang), angle=bang,
           sx=1.12, sy=1.12 * (1 + 0.09 * math.cos(4 * math.pi * p)))

    draw_leg(c, p, HIP_N, bpos, bang, far=False)
    draw_arm(c, p, SHO_N, bpos, bang, far=False)
    return c.image()
