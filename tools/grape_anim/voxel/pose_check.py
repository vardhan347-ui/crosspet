"""Side-by-side of the assembled rig against the hero render.

This is the calibration harness. The parts sheet lays each piece out at its own
scale, so swagger.py's per-part scales (BODY_S, LEG_S, ARM_S, SPRIG_S, EYES_S,
MOUTH_S) and its body-local anchors were tuned by eye against this comparison.
Re-run it after touching any of them.

    python3 pose_check.py [hero.png]
"""
import math, sys, os
from PIL import Image
import swagger as S
from rig import Canvas

HERO = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('HERO', '')


def standing():
    """Neutral A-pose at the same proportions the walk uses."""
    S.BODY_SX = S.BODY_SY = 1.0
    b = (S.CENTER_X, S.HIP_Y)
    c = Canvas(S.W, S.H)
    c.draw('arm_l', S.ARM_SHO, S.local_to_world(S.SHO_F, b, 0), angle=8,
           sx=S.ARM_S, sy=S.ARM_S, shade=S.SHADE_FAR)
    for side, hip, dx, far in (('F', S.HIP_F, -62, True), ('N', S.HIP_N, 62, False)):
        hx, hy = S.local_to_world(hip, b, 0)
        fx, fy = S.CENTER_X + dx, S.ANKLE_Y
        st = math.hypot(fx - hx, fy - hy) / S.TUBE_LEN
        ang = math.degrees(math.atan2(fx - hx, fy - hy))
        sh = S.SHADE_FAR if far else 1.0
        c.draw('leg_tube', S.TUBE_HIP, (hx, hy), angle=ang,
               sx=S.LEG_S, sy=st * S.LEG_S, shade=sh)
        ax = hx + math.sin(math.radians(ang)) * S.TUBE_LEN * st
        ay = hy + math.cos(math.radians(ang)) * S.TUBE_LEN * st
        c.draw('leg_shoe', S.SHOE_ANKLE, (ax, ay), angle=ang * 0.5,
               sx=S.SHOE_SX, sy=S.SHOE_SY, shade=sh)
        if far:
            c.draw('sprig', S.SPRIG_BASE, S.local_to_world(S.SPRIG_A, b, 0),
                   sx=S.SPRIG_S, sy=S.SPRIG_S)
            c.draw('body', S.BODY_ORIGIN, b, sx=S.BODY_S, sy=S.BODY_S)
            c.draw('eyes_happy', S.EYES_PIV, S.local_to_world(S.EYES, b, 0),
                   sx=S.EYES_S, sy=S.EYES_S)
            c.draw('mouth_open', S.MOUTH_PIV, S.local_to_world(S.MOUTH, b, 0),
                   sx=S.MOUTH_S, sy=S.MOUTH_S)
            c.draw('arm_r', S.ARM_SHO, S.local_to_world(S.SHO_N, b, 0), angle=-8,
                   sx=S.ARM_S, sy=S.ARM_S)
    return c.image()


im = standing()
im = im.crop(im.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox())
TH = 760
mine = im.resize((int(im.width * TH / im.height), TH), Image.LANCZOS)

if HERO and os.path.exists(HERO):
    hero = Image.open(HERO).convert('RGB').crop((280, 30, 1100, 1210))
    hero = hero.resize((int(hero.width * TH / hero.height), TH), Image.LANCZOS)
    out = Image.new('RGB', (hero.width + mine.width + 30, TH), (250, 248, 252))
    out.paste(hero, (0, 0))
    out.paste(mine, (hero.width + 30, 0), mine)
else:
    out = Image.new('RGB', mine.size, (250, 248, 252))
    out.paste(mine, (0, 0), mine)
    print('no hero render given; rendering the rig alone')
out.save('pose_check.png')
print('wrote pose_check.png', out.size)
