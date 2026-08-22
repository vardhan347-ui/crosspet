import base64, json, math, sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'voxel')
import walk
import swagger as vx

OUT = '/tmp/claude-0/-home-user-crosspet/8da4bd28-0960-5873-9c8e-665b216ed1cc/scratchpad/grape_walk_cycle.html'

def b64(p, mime='image/png'):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()

# ---------- build 01: the flat cycle ----------------------------------
m1 = json.load(open('out/web/meta.json'))
FW1, FH1, N1 = m1['frameW'], m1['frameH'], m1['frames']
STRIP1 = b64('out/web/strip_small.webp', 'image/webp')
GPF1 = 2 * walk.STRIDE * (FW1 / 851.0) / 12.0

PARTS1 = [('body', 'Body', 'Bobs twice a stride, squashes into each contact.'),
          ('leg_tube', 'Shin', 'Rotates and stretches to reach the foot.'),
          ('leg_shoe', 'Shoe', 'Rolls on its own: toe up at heel strike, down at push-off.'),
          ('arm_hang', 'Arm', 'One asset, mirrored. Swings against its own leg.'),
          ('vine', 'Vine', 'Trails the bob by a fifth of a cycle.'),
          ('leaf', 'Leaf', 'Same drag, doubled.'),
          ('eyes_happy', 'Eyes', 'Open for 22 of the 24 frames.'),
          ('eyes_closed', 'Eyes, shut', 'Frames 16 and 17 — the blink.'),
          ('mouth_open_big', 'Mouth', 'Scaled on the bob so the jaw carries the impact.')]
IMG1 = {n: b64(f'out/web/part_{n}.png') for n, _, _ in PARTS1}

path = []
for i in range(97):
    f, l = walk.foot_path(i / 96)
    path.append(f'{f:.1f},{-l:.1f}')
STANCE_PTS, SWING_PTS = ' '.join(path[:49]), ' '.join(path[48:])

# ---------- build 02: the voxel swagger -------------------------------
m2 = json.load(open('voxel/out/web/meta.json'))
FW2, FH2, N2 = m2['frameW'], m2['frameH'], m2['frames']
STRIP2 = b64('voxel/out/web/strip_small.webp', 'image/webp')
GPF2 = vx.STRIDE * (FW2 / 933.0) / (vx.N_FRAMES / 2.0)

PARTS2 = [('body', 'Body', 'Four bobs a stride — the double bounce.'),
          ('leg_tube', 'Shin', 'A rigid column. Stretches instead of bending.'),
          ('leg_shoe', 'Shoe', 'Rolls on the ankle disc.'),
          ('arm_l', 'Arm, raised', 'Stands in for the reference’s pointing finger.'),
          ('arm_r', 'Arm, sweeping', 'One slow gesture across the whole loop.'),
          ('sprig', 'Sprig', 'Vine and leaf in one piece; drags behind the bob.'),
          ('eyes_happy', 'Eyes', 'Held for 45 of the 53 frames.'),
          ('eyes_wide', 'Eyes, wide', 'Frames 22–29 — the reference’s expression beat.'),
          ('mouth_open', 'Mouth', 'Rides the head drift.')]
IMG2 = {n: b64(f'voxel/out/web/part_{n}.png') for n, _, _ in PARTS2}

CURVES = json.load(open('voxel/ref_curves.json'))
def series(key, lo, hi, w, h):
    pts = []
    for k in CURVES:
        x = k['f'] / (len(CURVES) - 1) * w
        y = h - (k[key] - lo) / (hi - lo) * h
        pts.append(f'{x:.1f},{y:.1f}')
    return ' '.join(pts)
CW, CH = 300.0, 62.0
BOB = series('bdy', -25, 32, CW, CH)
LEAN = series('brot', -14, -2, CW, CH)
SWEEP = series('sweep', -14, 106, CW, CH)

# ---------- cel grids -------------------------------------------------
def cels(n, cell_w, contact, passing, special, tag_special):
    out = []
    for i in range(n):
        kind = 'contact' if i in contact else 'pass' if i in passing else ''
        tag = 'contact' if i in contact else 'passing' if i in passing else ''
        sp = ' special' if i in special else ''
        out.append(
            f'<button class="cel {kind}{sp}" data-f="{i}" type="button" '
            f'aria-label="Frame {i}{" — " + tag if tag else ""}">'
            f'<span class="cel-img" style="background-position:{-i * cell_w}px 0"></span>'
            f'<span class="cel-n">{i:02d}</span>'
            f'{f"<span class=cel-tag>{tag}</span>" if tag else ""}'
            f'{f"<span class=cel-flag>{tag_special}</span>" if i in special else ""}'
            '</button>')
    return '\n'.join(out)

CELS1 = cels(N1, 108, {0, 6, 12, 18}, {3, 9, 15, 21}, {16, 17}, 'blink')
CELS2 = cels(N2, 70, {0, 26}, {13, 40}, set(range(22, 30)), 'eyes')

def cards(parts, imgs):
    return '\n'.join(
        f'''<figure class="part">
      <div class="part-img"><img src="{imgs[n]}" alt="{lab} cut-out"></div>
      <figcaption><span class="part-name">{lab}</span><span class="part-role">{role}</span></figcaption>
    </figure>''' for n, lab, role in parts)

HTML = f'''<title>Grape Walk Cycle</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Titan+One&family=Archivo:wght@400;500;600;800&family=Space+Mono:wght@400;700&display=swap">
<style>
:root {{
  --ground:#F3EEF8; --panel:#FFFFFF; --panel-2:#EBE1F3; --line:#DBCDE8;
  --ink:#1F1029; --ink-2:#5F4C6E; --ink-3:#8A7899;
  --accent:#7B2FD6; --accent-2:#B472FF; --accent-soft:#EFE1FF;
  --leaf:#3B8B2C; --hot:#CE1F66;
  --stage-1:#EDE1F8; --stage-2:#DCC9EE; --glow:rgba(150,74,224,.34);
  --shadow:0 1px 2px rgba(31,16,41,.06), 0 12px 34px -18px rgba(31,16,41,.34);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#140A1B; --panel:#1E1128; --panel-2:#2A1737; --line:#3B2551;
    --ink:#F4ECFA; --ink-2:#AE97C1; --ink-3:#7C6690;
    --accent:#B472FF; --accent-2:#D9AEFF; --accent-soft:#33204A;
    --leaf:#78D962; --hot:#FF548F;
    --stage-1:#241234; --stage-2:#120817; --glow:rgba(163,90,238,.42);
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 16px 40px -20px rgba(0,0,0,.8);
  }}
}}
:root[data-theme="dark"] {{
  --ground:#140A1B; --panel:#1E1128; --panel-2:#2A1737; --line:#3B2551;
  --ink:#F4ECFA; --ink-2:#AE97C1; --ink-3:#7C6690;
  --accent:#B472FF; --accent-2:#D9AEFF; --accent-soft:#33204A;
  --leaf:#78D962; --hot:#FF548F;
  --stage-1:#241234; --stage-2:#120817; --glow:rgba(163,90,238,.42);
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 16px 40px -20px rgba(0,0,0,.8);
}}
*,*::before,*::after {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font-family:Archivo,"Helvetica Neue",Arial,sans-serif; font-size:16px; line-height:1.62;
  -webkit-font-smoothing:antialiased; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:clamp(28px,5vw,64px) clamp(18px,4vw,40px) 96px; }}
section {{ margin-top:clamp(52px,7vw,88px); }}
.eyebrow {{ font-family:"Space Mono",ui-monospace,monospace; font-size:12px; font-weight:700;
  letter-spacing:.16em; text-transform:uppercase; color:var(--accent); margin:0 0 10px; }}
h1 {{ font-family:"Titan One",Archivo,sans-serif; font-weight:400;
  font-size:clamp(40px,7.4vw,76px); line-height:.94; letter-spacing:-.01em;
  margin:0 0 18px; text-wrap:balance; }}
h1 em {{ font-style:normal; color:var(--accent); }}
h2 {{ font-family:Archivo,sans-serif; font-weight:800; font-size:clamp(22px,3.2vw,30px);
  letter-spacing:-.015em; line-height:1.15; margin:0 0 8px; text-wrap:balance; }}
h3 {{ font-family:Archivo,sans-serif; font-weight:800; font-size:17px; margin:0 0 6px; }}
.lede {{ max-width:60ch; color:var(--ink-2); font-size:clamp(16px,1.7vw,18.5px); margin:0; }}
.sec-head {{ margin-bottom:26px; }}
.sec-head p {{ max-width:62ch; color:var(--ink-2); margin:6px 0 0; }}
.build {{ display:flex; align-items:baseline; gap:12px; }}
.build .no {{ font-family:"Space Mono",monospace; font-size:12px; font-weight:700;
  letter-spacing:.16em; color:var(--ink-3); }}

.stage {{ margin-top:30px; position:relative; overflow:hidden; border:1px solid var(--line);
  border-radius:20px; background:radial-gradient(120% 96% at 50% 8%, var(--stage-1), var(--stage-2));
  box-shadow:var(--shadow); }}
.stage::before {{ content:""; position:absolute; inset:0;
  background:radial-gradient(46% 52% at 50% 62%, var(--glow), transparent 72%); pointer-events:none; }}
.floor {{ position:absolute; left:0; right:0; bottom:68px; height:11px;
  background-image:repeating-linear-gradient(90deg, currentColor 0 26px, transparent 26px 72px);
  color:var(--accent); opacity:.30;
  mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent); }}
.floor.b {{ bottom:66px; height:2px; opacity:.34; background-image:none; background-color:currentColor;
  mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent); }}
.walker {{ position:relative; margin:26px auto 34px; background-repeat:no-repeat; }}
.w1 {{ width:{FW1}px; height:{FH1}px; background-image:url({STRIP1}); background-size:{FW1*N1}px {FH1}px; }}
.w2 {{ width:{FW2}px; height:{FH2}px; background-image:url({STRIP2}); background-size:{FW2*N2}px {FH2}px; }}
@media (max-width:520px) {{ .walker {{ transform:scale(.74); transform-origin:bottom center; margin-bottom:6px; }} }}

.bench {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px 18px; padding:14px 18px;
  border-top:1px solid var(--line); background:var(--panel);
  background:color-mix(in srgb, var(--panel) 76%, transparent);
  backdrop-filter:blur(6px); position:relative; }}
.bench .spacer {{ flex:1 1 auto; }}
button {{ font:inherit; color:inherit; }}
.btn {{ display:inline-flex; align-items:center; gap:8px; padding:8px 16px; cursor:pointer;
  border:1px solid var(--line); border-radius:999px; background:var(--panel);
  font-weight:600; font-size:14px; transition:background .15s, border-color .15s, color .15s; }}
.btn:hover {{ border-color:var(--accent); color:var(--accent); }}
.btn.primary {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
.btn.primary:hover {{ background:var(--accent-2); border-color:var(--accent-2); color:#1F1029; }}
.rate {{ display:flex; border:1px solid var(--line); border-radius:999px; overflow:hidden; background:var(--panel); }}
.rate button {{ border:0; background:transparent; padding:8px 14px; cursor:pointer;
  font-family:"Space Mono",monospace; font-size:13px; }}
.rate button + button {{ border-left:1px solid var(--line); }}
.rate button[aria-pressed="true"] {{ background:var(--accent); color:#fff; }}
.readout {{ font-family:"Space Mono",monospace; font-size:13px; color:var(--ink-2);
  font-variant-numeric:tabular-nums; letter-spacing:.02em; }}
.readout b {{ color:var(--ink); font-weight:700; }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:6px; }}

.legend {{ display:flex; flex-wrap:wrap; gap:8px 20px; margin:22px 0 14px; padding:0; list-style:none; }}
.legend li {{ display:flex; align-items:center; gap:8px; font-family:"Space Mono",monospace;
  font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-2); }}
.swatch {{ width:22px; height:3px; border-radius:2px; background:var(--line); }}
.swatch.c {{ background:var(--accent); }} .swatch.p {{ background:var(--ink-3); }}
.swatch.b {{ background:var(--hot); }}
.sheet {{ display:grid; gap:8px; border:1px solid var(--line); border-radius:16px; padding:12px;
  background:var(--panel); box-shadow:var(--shadow); }}
.sheet.g8 {{ grid-template-columns:repeat(8,minmax(0,1fr)); }}
.sheet.g11 {{ grid-template-columns:repeat(11,minmax(0,1fr)); }}
@media (max-width:820px) {{ .sheet.g8 {{ grid-template-columns:repeat(4,minmax(0,1fr)); }}
  .sheet.g11 {{ grid-template-columns:repeat(6,minmax(0,1fr)); }} }}
.cel {{ position:relative; display:block; width:100%; padding:0 0 6px; cursor:pointer;
  border:1px solid transparent; border-top:3px solid var(--line); border-radius:0 0 8px 8px;
  background:var(--panel-2); transition:background .15s, border-color .15s; }}
.cel.contact {{ border-top-color:var(--accent); }}
.cel.pass {{ border-top-color:var(--ink-3); }}
.cel:hover, .cel[aria-current="true"] {{ background:var(--accent-soft); border-color:var(--accent); }}
.cel-img {{ display:block; width:100%; background-repeat:no-repeat; }}
.sheet.g8 .cel-img {{ height:120px; background-image:url({STRIP1}); background-size:{108*N1}px 120px; }}
.sheet.g11 .cel-img {{ height:92px; background-image:url({STRIP2}); background-size:{70*N2}px 92px; }}
.cel-n {{ display:block; font-family:"Space Mono",monospace; font-size:11px; font-weight:700;
  letter-spacing:.06em; color:var(--ink-2); font-variant-numeric:tabular-nums; }}
.cel-tag {{ display:block; font-family:"Space Mono",monospace; font-size:9px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3); }}
.cel-flag {{ position:absolute; top:5px; right:5px; padding:1px 5px; border-radius:999px;
  background:var(--hot); color:#fff; font-family:"Space Mono",monospace; font-size:9px;
  letter-spacing:.06em; text-transform:uppercase; }}

.parts {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:14px; }}
.part {{ margin:0; border:1px solid var(--line); border-radius:14px; overflow:hidden;
  background:var(--panel); display:flex; flex-direction:column; }}
.part-img {{ height:128px; display:grid; place-items:center; padding:12px;
  background:radial-gradient(70% 70% at 50% 45%, var(--accent-soft), transparent 78%); }}
.part-img img {{ max-width:100%; max-height:104px; display:block; }}
.part figcaption {{ padding:12px 14px 15px; border-top:1px solid var(--line); }}
.part-name {{ display:block; font-weight:700; font-size:14.5px; }}
.part-role {{ display:block; margin-top:3px; font-size:13px; line-height:1.5; color:var(--ink-2); }}

.two {{ display:grid; grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);
  gap:clamp(20px,4vw,44px); align-items:center; }}
@media (max-width:760px) {{ .two {{ grid-template-columns:1fr; }} }}
.fig {{ border:1px solid var(--line); border-radius:16px; background:var(--panel);
  padding:18px; box-shadow:var(--shadow); }}
.fig svg {{ display:block; width:100%; height:auto; }}
.two p {{ color:var(--ink-2); margin:0 0 14px; max-width:56ch; }}
.two p:last-child {{ margin-bottom:0; }}
.two strong {{ color:var(--ink); font-weight:600; }}
.note {{ font-family:"Space Mono",monospace; font-size:12.5px; line-height:1.7; color:var(--ink-2); }}

.files {{ border:1px solid var(--line); border-radius:16px; overflow:hidden; background:var(--panel); }}
.files table {{ width:100%; border-collapse:collapse; font-size:14.5px; }}
.files th, .files td {{ text-align:left; padding:11px 16px; border-bottom:1px solid var(--line);
  vertical-align:top; }}
.files tr:last-child td {{ border-bottom:0; }}
.files th {{ font-family:"Space Mono",monospace; font-size:11px; font-weight:700; letter-spacing:.12em;
  text-transform:uppercase; color:var(--ink-3); background:var(--panel-2); }}
.files td:first-child {{ font-family:"Space Mono",monospace; font-size:13px; color:var(--accent); white-space:nowrap; }}
.files td:last-child {{ color:var(--ink-2); }}
.scrollx {{ overflow-x:auto; }}
code {{ font-family:"Space Mono",ui-monospace,monospace; font-size:.9em; color:var(--accent);
  background:var(--accent-soft); padding:1px 6px; border-radius:5px; }}
.curves {{ display:grid; gap:14px; }}
.curve {{ border:1px solid var(--line); border-radius:12px; background:var(--panel); padding:12px 14px; }}
.curve b {{ font-family:"Space Mono",monospace; font-size:11px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); font-weight:700; }}
.curve span {{ display:block; font-size:13.5px; color:var(--ink-2); margin:2px 0 6px; }}
footer {{ margin-top:56px; padding-top:22px; border-top:1px solid var(--line); }}
footer p {{ margin:0; font-family:"Space Mono",monospace; font-size:12px; letter-spacing:.05em; color:var(--ink-3); }}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">two builds · both cut from a parts sheet</p>
    <h1>The grape<br><em>goes for a walk</em></h1>
    <p class="lede">Neither of these was drawn. Each frame is the character's own
    parts sheet, cut apart at the alpha and put back together — first as a walk
    built from scratch, then as the swagger from an After Effects rig, retargeted
    onto the voxel model.</p>
  </header>

  <section>
    <div class="sec-head">
      <div class="build"><span class="no">Build 01</span></div>
      <h2>A cycle from scratch</h2>
      <p>24 frames at 12 fps, two strides, walking right. The blink is the only
      thing in it that doesn't repeat every twelve frames.</p>
    </div>
    <div class="stage">
      <div class="floor" id="floor1"></div><div class="floor b"></div>
      <div class="walker w1" id="walker1"></div>
      <div class="bench">
        <button class="btn primary" id="play1" type="button">Pause</button>
        <div class="rate" role="group" aria-label="Playback rate" id="rate1">
          <button type="button" data-fps="6">6 fps</button>
          <button type="button" data-fps="12" aria-pressed="true">12 fps</button>
          <button type="button" data-fps="24">24 fps</button>
        </div>
        <span class="spacer"></span>
        <span class="readout">frame <b id="fnum1">00</b> / {N1-1} &nbsp;·&nbsp; <span id="phase1">contact</span></span>
      </div>
    </div>
    <ul class="legend">
      <li><span class="swatch c"></span>Contact</li>
      <li><span class="swatch p"></span>Passing</li>
      <li><span class="swatch"></span>In-between</li>
      <li><span class="swatch b"></span>Blink</li>
    </ul>
    <div class="sheet g8" id="sheet1">
{CELS1}
    </div>
  </section>

  <section>
    <div class="two">
      <div class="fig">
        <svg viewBox="-118 -206 236 96" role="img" aria-label="The foot path: a flat planted stance line and a raised swing arc, with the shin solving from hip to foot">
          <line x1="-112" y1="-128.5" x2="112" y2="-128.5" stroke="var(--line)" stroke-width="1.6"/>
          <g transform="translate(0,-130)">
            <g stroke="var(--accent)" stroke-width="1.4" opacity=".55" stroke-linecap="round">
              <line x1="0" y1="-58" x2="92" y2="0"/><line x1="0" y1="-58" x2="0" y2="-16.7"/>
            </g>
            <polyline points="{SWING_PTS}" fill="none" stroke="var(--accent)" stroke-width="2.4"
                      stroke-dasharray="5 4.5" stroke-linecap="round" transform="scale(1,0.334)"/>
            <polyline points="{STANCE_PTS}" fill="none" stroke="var(--accent)" stroke-width="3.4"
                      stroke-linecap="round" transform="scale(1,0.334)"/>
            <circle cx="0" cy="-58" r="4.4" fill="var(--accent)"/>
            <text x="0" y="-64" text-anchor="middle" fill="var(--ink-2)" font-family="Space Mono, monospace" font-size="7" letter-spacing="1">HIP</text>
            <circle cx="92" cy="0" r="3.4" fill="var(--hot)"/><circle cx="0" cy="-16.7" r="3.4" fill="var(--hot)"/>
            <text x="-58" y="12" text-anchor="middle" fill="var(--ink-3)" font-family="Space Mono, monospace" font-size="6.4" letter-spacing="1.2">STANCE</text>
            <text x="0" y="-27" text-anchor="middle" fill="var(--ink-3)" font-family="Space Mono, monospace" font-size="6.4" letter-spacing="1.2">SWING</text>
          </g>
        </svg>
      </div>
      <div>
        <p class="eyebrow">The leg</p>
        <h3>The foot leads, the leg follows</h3>
        <p>Nothing swings the leg. Each foot is given a <strong>path</strong> —
        planted and sliding straight back for half the cycle, then lifting through
        a smoothstep arc — and the shin solves for whatever angle and length reach
        it. That length is the trick: longest when the foot is out at contact,
        shortest as it passes under the body. <strong>Straight at contact, short at
        passing</strong>, with no knee in the rig.</p>
        <p class="note">the shin ends in a disc centred on the ankle pivot — a disc
        on the pivot is rotation-invariant, so the shoe can roll as far as it likes
        and never uncovers the cut. Both builds use it.</p>
      </div>
    </div>
    <div class="parts" style="margin-top:26px">
{cards(PARTS1, IMG1)}
    </div>
  </section>

  <section>
    <div class="sec-head">
      <div class="build"><span class="no">Build 02</span></div>
      <h2>Your Lottie, on the voxel model</h2>
      <p>53 frames at 30 fps, one stride, walking left. The performance is read
      straight out of <code>Bud_Leaf_2.json</code> — loaded in a headless browser
      with lottie-web, stepped a frame at a time, each layer's composed transform
      matrix taken off the rendered SVG. No keyframe interpolation reimplemented,
      no parenting guessed at.</p>
    </div>
    <div class="stage">
      <div class="floor" id="floor2"></div><div class="floor b"></div>
      <div class="walker w2" id="walker2"></div>
      <div class="bench">
        <button class="btn primary" id="play2" type="button">Pause</button>
        <div class="rate" role="group" aria-label="Playback rate" id="rate2">
          <button type="button" data-fps="12">12 fps</button>
          <button type="button" data-fps="30" aria-pressed="true">30 fps</button>
          <button type="button" data-fps="60">60 fps</button>
        </div>
        <span class="spacer"></span>
        <span class="readout">frame <b id="fnum2">00</b> / {N2-1} &nbsp;·&nbsp; <span id="phase2">contact</span></span>
      </div>
    </div>
    <ul class="legend">
      <li><span class="swatch c"></span>Contact</li>
      <li><span class="swatch p"></span>Passing</li>
      <li><span class="swatch"></span>In-between</li>
      <li><span class="swatch b"></span>Wide eyes</li>
    </ul>
    <div class="sheet g11" id="sheet2">
{CELS2}
    </div>
  </section>

  <section>
    <div class="sec-head">
      <p class="eyebrow">Read off your file</p>
      <h2>Three curves that make it a swagger</h2>
      <p>These are plotted from <code>ref_curves.json</code> — the numbers pulled
      out of the Lottie, not an approximation of them.</p>
    </div>
    <div class="curves">
      <div class="curve">
        <b>Body height</b>
        <span>Four bobs per stride, not two. That double bounce is the strut — a
        plain walk would rise once per step.</span>
        <svg viewBox="-4 -6 308 74" role="img" aria-label="Body height over the loop: four bounces">
          <polyline points="{BOB}" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="curve">
        <b>Body lean</b>
        <span>One slow sway from −3° to −13° and back, spanning the whole loop
        rather than resetting each step.</span>
        <svg viewBox="-4 -6 308 74" role="img" aria-label="Body lean over the loop: a single slow ramp">
          <polyline points="{LEAN}" fill="none" stroke="var(--leaf)" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="curve">
        <b>Arm sweep</b>
        <span>0° to 103° and back, once. This arm never swings with the legs — it
        makes one slow gesture across the entire stride.</span>
        <svg viewBox="-4 -6 308 74" role="img" aria-label="Arm rotation over the loop: one slow arc">
          <polyline points="{SWEEP}" fill="none" stroke="var(--hot)" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <div class="two" style="margin-top:32px">
      <div>
        <h3>What had to change</h3>
        <p>The reference animates its legs by <strong>morphing a noodle outline</strong>
        — the shin curves through an S and the foot rolls off the toe. A voxel shin
        is a rigid column, so the legs are re-solved as the same one-bone IK as
        Build 01, against the reference's own stride, stance/swing split and contact
        phasing.</p>
        <p>Two things are deliberately scaled back. The full 255px stride, which the
        reference reaches by curving, reads as the splits on a straight column — it
        runs at <strong>58%</strong>. And the arm sweep runs at <strong>50%</strong>:
        a rigid arm swung the full 103° lies across the character's own face.</p>
        <p>The reference points with an extended index finger. The parts sheet has no
        pointing hand, so the hanging arm is rotated up instead — close in silhouette,
        and it holds the same beat.</p>
      </div>
      <div>
        <h3>One more catch</h3>
        <p>The parts sheet lays each piece out at whatever size suited the layout,
        not at assembly scale — the body is drawn noticeably smaller relative to the
        limbs than it appears assembled. Scaling everything uniformly gives a
        pinheaded grape on stilts.</p>
        <p>So body, legs, arms, sprig and face each carry their own scale, measured
        off the hero render: shin width, body extent, sprig bounding box, the span of
        the eye whites and of the tongue. <code>pose_check.py</code> stands the
        assembled rig next to that render so the numbers can be checked by eye.</p>
        <p class="note">voxels have to stay cubes — every part scale is uniform, never
        stretched on one axis.</p>
      </div>
    </div>
    <div class="parts" style="margin-top:26px">
{cards(PARTS2, IMG2)}
    </div>
  </section>

  <section>
    <div class="sec-head">
      <p class="eyebrow">Delivered</p>
      <h2>What came out of it</h2>
      <p>All of it lives in <code>tools/grape_anim/</code> on the
      <code>claude/grape-walking-animation-mq1ehb</code> branch.</p>
    </div>
    <div class="files scrollx">
      <table>
        <thead><tr><th>Path</th><th>What it is</th></tr></thead>
        <tbody>
          <tr><td>out/grape_walk.gif</td><td>Build 01 — 24 frames, 12 fps, matted</td></tr>
          <tr><td>out/grape_walk.webp</td><td>Build 01 with a real alpha channel</td></tr>
          <tr><td>out/grape_walk_sheet.png</td><td>Build 01 sprite sheet, 8 × 3, 470 × 520 per cel</td></tr>
          <tr><td>voxel/out/grape_swagger.gif</td><td>Build 02 — 53 frames, 30 fps, matted</td></tr>
          <tr><td>voxel/out/grape_swagger.webp</td><td>Build 02 with a real alpha channel</td></tr>
          <tr><td>voxel/out/grape_swagger_sheet.png</td><td>Build 02 sprite sheet, 8 × 7, 230 × 300 per cel</td></tr>
          <tr><td>voxel/ref_curves.json</td><td>The performance read out of your Lottie</td></tr>
          <tr><td>voxel/extract_ref.py</td><td>Reads it — headless Chromium plus lottie-web</td></tr>
          <tr><td>parts/ · voxel/parts/</td><td>37 and 21 cut-outs from the two sheets</td></tr>
          <tr><td>walk.py · voxel/swagger.py</td><td>The two rigs; gait tuning at the top of each</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <footer><p>Rigged from the parts sheets · CrossPet</p></footer>
</div>

<script>
(function () {{
  function Player(o) {{
    var walker = document.getElementById(o.walker),
        floor = document.getElementById(o.floor),
        fnum = document.getElementById(o.fnum),
        phase = document.getElementById(o.phase),
        playBtn = document.getElementById(o.play),
        rate = document.getElementById(o.rate),
        cels = Array.prototype.slice.call(document.querySelectorAll('#' + o.sheet + ' .cel'));
    var fps = o.fps, elapsed = 0, last = null, pinned = null;
    var playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function label(f) {{
      if (o.contact.indexOf(f) > -1) return 'contact';
      if (o.passing.indexOf(f) > -1) return 'passing';
      return (f >= o.sp0 && f <= o.sp1) ? o.spName : 'in-between';
    }}
    function show(f, ground) {{
      walker.style.backgroundPosition = (-f * o.fw) + 'px 0';
      floor.style.backgroundPositionX = (-ground) + 'px';
      fnum.textContent = f < 10 ? '0' + f : '' + f;
      phase.textContent = label(f);
      for (var i = 0; i < cels.length; i++)
        cels[i].setAttribute('aria-current', i === f ? 'true' : 'false');
    }}
    function tick(t) {{
      if (last === null) last = t;
      var dt = Math.min((t - last) / 1000, 0.25); last = t;
      if (playing && pinned === null) {{
        elapsed += dt * fps;
        show(Math.floor(elapsed) % o.n, elapsed * o.gpf);
      }}
      requestAnimationFrame(tick);
    }}
    playBtn.addEventListener('click', function () {{
      if (playing && pinned === null) {{ playing = false; }}
      else {{ playing = true; pinned = null; }}
      playBtn.textContent = playing ? 'Pause' : 'Play';
    }});
    rate.querySelectorAll('button').forEach(function (b) {{
      b.addEventListener('click', function () {{
        fps = +b.dataset.fps;
        rate.querySelectorAll('button').forEach(function (x) {{
          x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
        }});
      }});
    }});
    cels.forEach(function (c, i) {{
      c.addEventListener('click', function () {{
        pinned = i; playing = false; playBtn.textContent = 'Play';
        show(i, elapsed * o.gpf);
      }});
    }});
    playBtn.textContent = playing ? 'Pause' : 'Play';
    show(0, 0);
    requestAnimationFrame(tick);
  }}

  Player({{walker:'walker1', floor:'floor1', fnum:'fnum1', phase:'phase1', play:'play1',
          rate:'rate1', sheet:'sheet1', n:{N1}, fw:{FW1}, gpf:{GPF1:.4f}, fps:12,
          contact:[0,6,12,18], passing:[3,9,15,21], sp0:16, sp1:17, spName:'blink'}});
  Player({{walker:'walker2', floor:'floor2', fnum:'fnum2', phase:'phase2', play:'play2',
          rate:'rate2', sheet:'sheet2', n:{N2}, fw:{FW2}, gpf:{GPF2:.4f}, fps:30,
          contact:[0,26], passing:[13,40], sp0:22, sp1:29, spName:'wide eyes'}});
}})();
</script>
'''
# the artifact wrapper owns <head>, so we cannot declare a charset -- write
# pure ASCII and let entities carry the punctuation
data = HTML.encode('ascii', 'xmlcharrefreplace')
open(OUT, 'wb').write(data)
print('wrote', OUT, f'{len(data)/1024/1024:.2f} MB')
