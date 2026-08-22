import base64, json, math, sys
sys.path.insert(0, '.')
import walk

OUT = '/tmp/claude-0/-home-user-crosspet/8da4bd28-0960-5873-9c8e-665b216ed1cc/scratchpad/grape_walk_cycle.html'

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()

meta = json.load(open('out/web/meta.json'))
FW, FH, N = meta['frameW'], meta['frameH'], meta['frames']
STRIP = b64('out/web/strip_small.png')

PARTS = [
    ('body',            'Body',        'Bobs twice a stride and squashes into each contact.'),
    ('leg_tube',        'Shin',        'Rotates and stretches to reach the foot; ends in a disc on the ankle pivot.'),
    ('leg_shoe',        'Shoe',        'Rolls on its own: toe up at heel strike, toe down through push-off.'),
    ('arm_hang',        'Arm',         'One asset, mirrored for the near side. Swings against its own leg.'),
    ('vine',            'Vine',        'Trails the bob by a fifth of a cycle.'),
    ('leaf',            'Leaf',        'Same drag, doubled — the loosest thing on the body.'),
    ('eyes_happy',      'Eyes',        'Held open for 22 of the 24 frames.'),
    ('eyes_closed',     'Eyes, shut',  'Swapped in for frames 16 and 17 — the blink.'),
    ('mouth_open_big',  'Mouth',       'Scaled on the bob so the jaw carries the impact.'),
]
part_imgs = {n: b64(f'out/web/part_{n}.png') for n, _, _ in PARTS}

path = []
for i in range(97):
    f, l = walk.foot_path(i / 96)
    path.append(f'{f:.1f},{-l:.1f}')
FOOT_PATH = ' '.join(path)
STANCE = ' '.join(path[:49])
SWING  = ' '.join(path[48:])

# preview px the ground travels per frame, so the scroll matches the stride
CANVAS_TO_PREVIEW = FW / 851.0
GROUND_PER_FRAME = 2 * walk.STRIDE * CANVAS_TO_PREVIEW / 12.0

CONTACT = {0, 6, 12, 18}
PASSING = {3, 9, 15, 21}
BLINK   = {16, 17}

cells = []
for i in range(N):
    kind = 'contact' if i in CONTACT else 'pass' if i in PASSING else ''
    tag  = 'contact' if i in CONTACT else 'passing' if i in PASSING else ''
    blink = ' blink' if i in BLINK else ''
    cells.append(
        f'<button class="cel {kind}{blink}" data-f="{i}" type="button" '
        f'aria-label="Frame {i}{" — " + tag if tag else ""}">'
        f'<span class="cel-img" style="background-position:{-i * 108}px 0"></span>'
        f'<span class="cel-n">{i:02d}</span>'
        f'{f"<span class=cel-tag>{tag}</span>" if tag else ""}'
        f'{"<span class=cel-blink>blink</span>" if i in BLINK else ""}'
        '</button>')
CELLS = '\n'.join(cells)

PART_CARDS = '\n'.join(
    f'''<figure class="part">
      <div class="part-img"><img src="{part_imgs[n]}" alt="{label} cut-out"></div>
      <figcaption><span class="part-name">{label}</span><span class="part-role">{role}</span></figcaption>
    </figure>''' for n, label, role in PARTS)

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
body {{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:Archivo,"Helvetica Neue",Arial,sans-serif;
  font-size:16px; line-height:1.62; -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:1080px; margin:0 auto; padding:clamp(28px,5vw,64px) clamp(18px,4vw,40px) 96px; }}
section {{ margin-top:clamp(52px,7vw,88px); }}

.eyebrow {{
  font-family:"Space Mono",ui-monospace,monospace; font-size:12px; font-weight:700;
  letter-spacing:.16em; text-transform:uppercase; color:var(--accent); margin:0 0 10px;
}}
h1 {{
  font-family:"Titan One",Archivo,sans-serif; font-weight:400;
  font-size:clamp(42px,8vw,82px); line-height:.94; letter-spacing:-.01em;
  margin:0 0 18px; text-wrap:balance;
}}
h1 em {{ font-style:normal; color:var(--accent); }}
h2 {{
  font-family:Archivo,sans-serif; font-weight:800; font-size:clamp(22px,3.2vw,30px);
  letter-spacing:-.015em; line-height:1.15; margin:0 0 8px; text-wrap:balance;
}}
.lede {{ max-width:60ch; color:var(--ink-2); font-size:clamp(16px,1.7vw,18.5px); margin:0; }}
.sec-head {{ margin-bottom:26px; }}
.sec-head p {{ max-width:62ch; color:var(--ink-2); margin:6px 0 0; }}

/* ---------- stage ---------- */
.stage {{
  margin-top:34px; position:relative; overflow:hidden; border:1px solid var(--line);
  border-radius:20px; background:radial-gradient(120% 96% at 50% 8%, var(--stage-1), var(--stage-2));
  box-shadow:var(--shadow);
}}
.stage::before {{
  content:""; position:absolute; inset:0;
  background:radial-gradient(46% 52% at 50% 62%, var(--glow), transparent 72%);
  pointer-events:none;
}}
.floor {{
  position:absolute; left:0; right:0; bottom:74px; height:64px;
  background-image:repeating-linear-gradient(90deg, currentColor 0 30px, transparent 30px 74px);
  color:var(--accent); opacity:.24; mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);
}}
.floor.b {{ bottom:66px; height:2px; opacity:.34; background-image:none; background-color:currentColor;
  mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent); }}
.walker {{
  position:relative; width:{FW}px; height:{FH}px; margin:26px auto 34px;
  background-image:url({STRIP}); background-repeat:no-repeat;
  background-size:{FW * N}px {FH}px; image-rendering:auto;
}}
@media (max-width:520px) {{ .walker {{ transform:scale(.78); transform-origin:bottom center; margin-bottom:8px; }} }}

.bench {{
  display:flex; flex-wrap:wrap; align-items:center; gap:10px 18px;
  padding:14px 18px; border-top:1px solid var(--line);
  background:var(--panel); background:color-mix(in srgb, var(--panel) 76%, transparent);
  backdrop-filter:blur(6px); position:relative;
}}
.bench .spacer {{ flex:1 1 auto; }}
button {{ font:inherit; color:inherit; }}
.btn {{
  display:inline-flex; align-items:center; gap:8px; padding:8px 16px; cursor:pointer;
  border:1px solid var(--line); border-radius:999px; background:var(--panel);
  font-weight:600; font-size:14px; transition:background .15s, border-color .15s, color .15s;
}}
.btn:hover {{ border-color:var(--accent); color:var(--accent); }}
.btn.primary {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
.btn.primary:hover {{ background:var(--accent-2); border-color:var(--accent-2); color:#1F1029; }}
.rate {{ display:flex; border:1px solid var(--line); border-radius:999px; overflow:hidden; background:var(--panel); }}
.rate button {{
  border:0; background:transparent; padding:8px 14px; cursor:pointer;
  font-family:"Space Mono",monospace; font-size:13px; letter-spacing:.02em;
}}
.rate button + button {{ border-left:1px solid var(--line); }}
.rate button[aria-pressed="true"] {{ background:var(--accent); color:#fff; }}
.readout {{
  font-family:"Space Mono",monospace; font-size:13px; color:var(--ink-2);
  font-variant-numeric:tabular-nums; letter-spacing:.02em;
}}
.readout b {{ color:var(--ink); font-weight:700; }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:6px; }}

/* ---------- dope sheet ---------- */
.legend {{ display:flex; flex-wrap:wrap; gap:8px 20px; margin:0 0 18px; padding:0; list-style:none; }}
.legend li {{ display:flex; align-items:center; gap:8px;
  font-family:"Space Mono",monospace; font-size:12px; letter-spacing:.06em;
  text-transform:uppercase; color:var(--ink-2); }}
.swatch {{ width:22px; height:3px; border-radius:2px; background:var(--line); }}
.swatch.c {{ background:var(--accent); }}
.swatch.p {{ background:var(--ink-3); }}
.swatch.b {{ background:var(--hot); }}
.sheet {{
  display:grid; grid-template-columns:repeat(8,minmax(0,1fr)); gap:8px;
  border:1px solid var(--line); border-radius:16px; padding:12px; background:var(--panel);
  box-shadow:var(--shadow);
}}
@media (max-width:820px) {{ .sheet {{ grid-template-columns:repeat(4,minmax(0,1fr)); }} }}
.cel {{
  position:relative; display:block; width:100%; padding:0 0 6px; cursor:pointer;
  border:1px solid transparent; border-top:3px solid var(--line); border-radius:0 0 8px 8px;
  background:var(--panel-2); transition:background .15s, border-color .15s;
}}
.cel.contact {{ border-top-color:var(--accent); }}
.cel.pass {{ border-top-color:var(--ink-3); }}
.cel:hover, .cel[aria-current="true"] {{ background:var(--accent-soft); border-color:var(--accent); }}
.cel-img {{
  display:block; width:100%; height:120px;
  background-image:url({STRIP}); background-repeat:no-repeat;
  background-size:{108 * N}px 120px;
}}
.cel-n {{
  display:block; font-family:"Space Mono",monospace; font-size:11px; font-weight:700;
  letter-spacing:.08em; color:var(--ink-2); font-variant-numeric:tabular-nums;
}}
.cel-tag {{ display:block; font-family:"Space Mono",monospace; font-size:9px;
  letter-spacing:.12em; text-transform:uppercase; color:var(--ink-3); }}
.cel-blink {{
  position:absolute; top:6px; right:6px; padding:1px 6px; border-radius:999px;
  background:var(--hot); color:#fff; font-family:"Space Mono",monospace;
  font-size:9px; letter-spacing:.08em; text-transform:uppercase;
}}

/* ---------- rig ---------- */
.parts {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(196px,1fr)); gap:14px; }}
.part {{
  margin:0; border:1px solid var(--line); border-radius:14px; overflow:hidden;
  background:var(--panel); display:flex; flex-direction:column;
}}
.part-img {{
  height:132px; display:grid; place-items:center; padding:12px;
  background:radial-gradient(70% 70% at 50% 45%, var(--accent-soft), transparent 78%);
}}
.part-img img {{ max-width:100%; max-height:108px; display:block; }}
.part figcaption {{ padding:12px 14px 15px; border-top:1px solid var(--line); }}
.part-name {{ display:block; font-weight:700; font-size:14.5px; letter-spacing:-.005em; }}
.part-role {{ display:block; margin-top:3px; font-size:13px; line-height:1.5; color:var(--ink-2); }}

/* ---------- solve ---------- */
.solve {{ display:grid; grid-template-columns:minmax(0,1.05fr) minmax(0,1fr); gap:clamp(20px,4vw,44px); align-items:center; }}
@media (max-width:760px) {{ .solve {{ grid-template-columns:1fr; }} }}
.solve-fig {{ border:1px solid var(--line); border-radius:16px; background:var(--panel); padding:18px; box-shadow:var(--shadow); }}
.solve-fig svg {{ display:block; width:100%; height:auto; }}
.solve p {{ color:var(--ink-2); margin:0 0 14px; max-width:56ch; }}
.solve p:last-child {{ margin-bottom:0; }}
.solve strong {{ color:var(--ink); font-weight:600; }}
.note {{
  font-family:"Space Mono",monospace; font-size:12.5px; line-height:1.7;
  letter-spacing:.01em; color:var(--ink-2);
}}

/* ---------- files ---------- */
.files {{ border:1px solid var(--line); border-radius:16px; overflow:hidden; background:var(--panel); }}
.files table {{ width:100%; border-collapse:collapse; font-size:14.5px; }}
.files th, .files td {{ text-align:left; padding:11px 16px; border-bottom:1px solid var(--line); }}
.files tr:last-child td {{ border-bottom:0; }}
.files th {{
  font-family:"Space Mono",monospace; font-size:11px; font-weight:700; letter-spacing:.12em;
  text-transform:uppercase; color:var(--ink-3); background:var(--panel-2);
}}
.files td:first-child {{ font-family:"Space Mono",monospace; font-size:13px; color:var(--accent); white-space:nowrap; }}
.files td:last-child {{ color:var(--ink-2); }}
.scrollx {{ overflow-x:auto; }}
code {{ font-family:"Space Mono",ui-monospace,monospace; font-size:.9em; color:var(--accent);
  background:var(--accent-soft); padding:1px 6px; border-radius:5px; }}
footer {{ margin-top:56px; padding-top:22px; border-top:1px solid var(--line); }}
footer p {{ margin:0; font-family:"Space Mono",monospace; font-size:12px; letter-spacing:.05em; color:var(--ink-3); }}
@media (prefers-reduced-motion:reduce) {{ .walker, .floor {{ transition:none; }} }}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">24 frames · 12 fps · two strides</p>
    <h1>The grape<br><em>goes for a walk</em></h1>
    <p class="lede">Every frame is the character parts sheet, cut apart and put back
    together. No drawing — the shin stretches, the shoe rolls, the leaf drags a
    beat behind, and the whole thing loops.</p>

    <div class="stage">
      <div class="floor" id="floor"></div>
      <div class="floor b" id="floorline"></div>
      <div class="walker" id="walker"></div>
      <div class="bench">
        <button class="btn primary" id="play" type="button">Pause</button>
        <div class="rate" role="group" aria-label="Playback rate">
          <button type="button" data-fps="8">8 fps</button>
          <button type="button" data-fps="12" aria-pressed="true">12 fps</button>
          <button type="button" data-fps="24">24 fps</button>
        </div>
        <span class="spacer"></span>
        <span class="readout">frame <b id="fnum">00</b> / 23 &nbsp;·&nbsp; <span id="phase">contact</span></span>
      </div>
    </div>
  </header>

  <section>
    <div class="sec-head">
      <p class="eyebrow">Exposure</p>
      <h2>Every frame in the loop</h2>
      <p>Pick any cel to hold the stage on it. Contacts and passing poses are the
      cycle's four beats; the blink is the only thing in here that does not repeat
      every twelve frames.</p>
    </div>
    <ul class="legend">
      <li><span class="swatch c"></span>Contact</li>
      <li><span class="swatch p"></span>Passing</li>
      <li><span class="swatch"></span>In-between</li>
      <li><span class="swatch b"></span>Blink</li>
    </ul>
    <div class="sheet" id="sheet">
{CELLS}
    </div>
  </section>

  <section>
    <div class="sec-head">
      <p class="eyebrow">Teardown</p>
      <h2>Nine pieces do all the work</h2>
      <p>The sheet yields 37 cut-outs — eight eye sets, sixteen mouths, a shelf of
      spare hands. The walk needs these.</p>
    </div>
    <div class="parts">
{PART_CARDS}
    </div>
  </section>

  <section>
    <div class="sec-head">
      <p class="eyebrow">The leg</p>
      <h2>The foot leads, the leg follows</h2>
    </div>
    <div class="solve">
      <div class="solve-fig">
        <svg viewBox="-118 -206 236 96" role="img" aria-label="Diagram of the foot path: a flat planted stance line and a raised swing arc, with the shin solving from the hip to each foot position">
          <line x1="-112" y1="-128.5" x2="112" y2="-128.5" stroke="var(--line)" stroke-width="1.6"/>
          <g transform="translate(0,-130)">
            <g stroke="var(--accent)" stroke-width="1.4" opacity=".55" stroke-linecap="round">
              <line x1="0" y1="-58" x2="92" y2="0"/>
              <line x1="0" y1="-58" x2="0" y2="-16.7"/>
            </g>
            <polyline points="{SWING}" fill="none" stroke="var(--accent)" stroke-width="2.4"
                      stroke-dasharray="5 4.5" stroke-linecap="round" stroke-linejoin="round"
                      transform="scale(1,0.334)"/>
            <polyline points="{STANCE}" fill="none" stroke="var(--accent)" stroke-width="3.4"
                      stroke-linecap="round" transform="scale(1,0.334)"/>
            <circle cx="0" cy="-58" r="4.4" fill="var(--accent)"/>
            <text x="0" y="-64" text-anchor="middle" fill="var(--ink-2)"
                  font-family="Space Mono, monospace" font-size="7" letter-spacing="1">HIP</text>
            <circle cx="92" cy="0" r="3.4" fill="var(--hot)"/>
            <circle cx="0" cy="-16.7" r="3.4" fill="var(--hot)"/>
            <text x="-58" y="12" text-anchor="middle" fill="var(--ink-3)"
                  font-family="Space Mono, monospace" font-size="6.4" letter-spacing="1.2">STANCE</text>
            <text x="0" y="-27" text-anchor="middle" fill="var(--ink-3)"
                  font-family="Space Mono, monospace" font-size="6.4" letter-spacing="1.2">SWING</text>
          </g>
        </svg>
      </div>
      <div>
        <p>Nothing swings the leg. Each foot is given a <strong>path</strong> — planted
        and sliding straight back for half the cycle, then lifting through a
        smoothstep arc to get out front again — and the shin solves for whatever
        angle and length reach it.</p>
        <p>That length is the whole trick. The shin is longest when the foot is far
        out at contact and shortest as it passes under the body, which is exactly
        the rubber-hose read: <strong>straight at contact, short at passing</strong>,
        with no knee anywhere in the rig.</p>
        <p class="note">shin ends in a disc centred on the ankle pivot — a disc on the
        pivot is rotation-invariant, so the shoe cuff can roll as far as it likes and
        never uncovers the cut.</p>
      </div>
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
        <thead><tr><th>File</th><th>What it is</th></tr></thead>
        <tbody>
          <tr><td>out/grape_walk.gif</td><td>The loop, matted on a light background</td></tr>
          <tr><td>out/grape_walk.webp</td><td>Same animation, real alpha channel</td></tr>
          <tr><td>out/grape_walk_sheet.png</td><td>Sprite sheet, 8 × 3, transparent, 470 × 520 per cel</td></tr>
          <tr><td>out/frames/walk_NN.png</td><td>The 24 frames on their own</td></tr>
          <tr><td>parts/</td><td>All 37 cut-outs from the sheet</td></tr>
          <tr><td>walk.py</td><td>The rig — stride, lift, bob and lean live at the top</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <footer><p>Rigged from the parts sheet · CrossPet</p></footer>
</div>

<script>
(function () {{
  var N = {N}, FW = {FW}, GPF = {GROUND_PER_FRAME:.4f};
  var CONTACT = [0, 6, 12, 18], PASSING = [3, 9, 15, 21];
  var walker = document.getElementById('walker');
  var floor = document.getElementById('floor');
  var fnum = document.getElementById('fnum');
  var phase = document.getElementById('phase');
  var playBtn = document.getElementById('play');
  var cels = Array.prototype.slice.call(document.querySelectorAll('.cel'));

  var fps = 12, elapsed = 0, last = null, pinned = null;
  var playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function label(f) {{
    if (CONTACT.indexOf(f) > -1) return 'contact';
    if (PASSING.indexOf(f) > -1) return 'passing';
    return (f === 16 || f === 17) ? 'blink' : 'in-between';
  }}

  function show(f, ground) {{
    walker.style.backgroundPosition = (-f * FW) + 'px 0';
    floor.style.backgroundPositionX = (-ground) + 'px';
    fnum.textContent = f < 10 ? '0' + f : '' + f;
    phase.textContent = label(f);
    for (var i = 0; i < cels.length; i++) {{
      cels[i].setAttribute('aria-current', i === f ? 'true' : 'false');
    }}
  }}

  function tick(t) {{
    if (last === null) last = t;
    var dt = Math.min((t - last) / 1000, 0.25);
    last = t;
    if (playing && pinned === null) {{
      elapsed += dt * fps;
      show(Math.floor(elapsed) % N, elapsed * GPF);
    }}
    requestAnimationFrame(tick);
  }}

  function setPlaying(on) {{
    playing = on;
    playBtn.textContent = on ? 'Pause' : 'Play';
    if (on) pinned = null;
  }}

  playBtn.addEventListener('click', function () {{ setPlaying(!playing || pinned !== null); }});

  document.querySelectorAll('.rate button').forEach(function (b) {{
    b.addEventListener('click', function () {{
      fps = +b.dataset.fps;
      document.querySelectorAll('.rate button').forEach(function (o) {{
        o.setAttribute('aria-pressed', o === b ? 'true' : 'false');
      }});
    }});
  }});

  cels.forEach(function (c, i) {{
    c.addEventListener('click', function () {{
      pinned = i;
      setPlaying(false);
      playing = false;
      playBtn.textContent = 'Play';
      show(i, elapsed * GPF);
    }});
  }});

  playBtn.textContent = playing ? 'Pause' : 'Play';
  show(0, 0);
  requestAnimationFrame(tick);
}})();
</script>
'''
open(OUT, 'w').write(HTML)
print('wrote', OUT, f'{len(HTML)/1024/1024:.2f} MB')
