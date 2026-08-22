# Grape walk cycle

A 24-frame walk cycle for the grape character, rigged and rendered from the
character parts sheet. Nothing is redrawn by hand — every frame is the sheet's
own cut-outs transformed and composited.

![walk cycle](out/grape_walk.gif)

## Output

| File | What it is |
|---|---|
| `out/grape_walk.gif` | 24 frames, 12 fps, looping, matted on a light background |
| `out/grape_walk.webp` | same animation with a real alpha channel |
| `out/grape_walk_sheet.png` | sprite sheet, 8 columns × 3 rows, transparent |
| `out/grape_walk_strip.png` | the same frames in one row, for CSS `steps()` |
| `out/frames/walk_NN.png` | the individual frames, transparent |

The strip and the individual frames are not checked in — they are the same
pixels as the sprite sheet and `python3 build.py` writes them back out.

Frames are 470 × 520. The cycle is two strides (12 frames each); frames 16–17
are a blink, so the loop does not read as perfectly mechanical.

## How it is rigged

`extract_parts.py` splits the parts sheet into `parts/*.png` by walking the
connected components of its alpha mask — 37 pieces (body, limbs, eight eye
sets, sixteen mouths, vine, leaf). The walk uses nine of them.

The leg is the only part that needed surgery. It is split at the ankle into
`leg_tube` and `leg_shoe` so the foot can roll independently of the shin. A
straight cut leaves a bright wedge poking out whenever the shoe rotates away
from the shin, so the tube instead ends in a **disc centred on the ankle
pivot**: a disc centred on the pivot is rotation-invariant, so once the
(slightly oversized) shoe cuff covers it, it can never uncover it.

Per frame, `walk.py`:

- puts each foot on a **path** rather than swinging the leg — planted and
  sliding backwards for the first half of the cycle, lifting through a
  smoothstep arc for the second — then solves the shin as a one-bone IK: the
  angle from hip to ankle, and a length scale that stretches the tube to reach.
  That stretch is what produces the rubber-hose "straight at contact, short at
  passing" read, with no knee to draw.
- bobs the body twice per stride (lowest at contact), with a little squash on
  the way down and a sway and forward lean on top.
- swings each arm against its own leg, with a few degrees of drag so the
  hand arrives late.
- trails the vine and leaf behind the bob for secondary motion.
- shades the far arm and leg to 72% to hold them back in depth, and drops a
  contact shadow that tightens as each foot lands.

`rig.py` is the compositor: one affine transform per part, straight to the
canvas, in premultiplied alpha so bicubic resampling cannot bleed the sheet's
dark background into the outlines.

## Rebuilding

```bash
pip install pillow numpy
python3 build.py            # frames + gif + webp + sheet + strip
python3 preview_assets.py   # small copies used by the preview page
python3 make_page.py        # self-contained HTML preview, assets inlined
```

`extract_parts.py <sheet.png>` only needs re-running if the parts sheet itself
changes; `parts/` is checked in.

Tuning lives at the top of `walk.py` — `STRIDE`, `LIFT`, `BOB`, `LEAN`,
`SHADE_FAR` — and the frame count and fps at the top of `build.py`.
