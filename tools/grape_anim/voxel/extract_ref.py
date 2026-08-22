"""Read the reference Lottie's performance out of a real Lottie render.

Rather than re-implementing bezier keyframe interpolation and layer parenting,
this loads `Bud_Leaf_2.json` in headless Chromium with lottie-web, steps a
frame at a time, and reads each layer group's composed transform matrix off
the rendered SVG. That gives the body, head, arm and sprig motion exactly as
After Effects authored it, parenting included.

Needs `lottie.min.js` beside this file:
    npm pack lottie-web@5.12.2 && tar xzf lottie-web-*.tgz
    cp package/build/player/lottie.min.js .

Writes `ref_curves.json`: one record per frame, body-relative and ready to
drive any character.
"""
import json, math, os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')

JS = r"""
(function(){
  var root = window.anim.renderer.elements[0];
  var comp = root.elements || [];
  var inv = document.querySelector('#c svg').getScreenCTM().inverse();
  var out = {};
  for (var i = 0; i < comp.length; i++) {
    var e = comp[i];
    if (!e || !e.layerElement || !e.data) continue;
    var m = inv.multiply(e.layerElement.getScreenCTM());
    out[e.data.nm] = {m: [m.a, m.b, m.c, m.d, m.e, m.f],
                      hidden: e.layerElement.style.display === 'none'};
  }
  return out;
})()
"""


def build_page():
    data = open(os.path.join(HERE, 'Bud_Leaf_2.json')).read()
    html = ('<!doctype html><meta charset="utf-8">'
            '<style>html,body{margin:0}#c{width:672px;height:672px}</style>'
            '<script src="lottie.min.js"></script><div id="c"></div><script>'
            'var DATA=' + data + ';'
            'window.anim=lottie.loadAnimation({container:document.getElementById("c"),'
            'renderer:"svg",loop:false,autoplay:false,animationData:DATA});'
            'window.ready=false;'
            'window.anim.addEventListener("DOMLoaded",function(){window.ready=true;});'
            'window.goto=function(f){window.anim.goToAndStop(f,true);};</script>')
    p = os.path.join(HERE, '_ref_page.html')
    open(p, 'w').write(html)
    return p


def main():
    page_path = build_page()
    n = json.load(open(os.path.join(HERE, 'Bud_Leaf_2.json')))['op']
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={'width': 672, 'height': 672})
        pg.goto('file://' + page_path)
        pg.wait_for_function('window.ready === true', timeout=60000)
        raw = []
        for f in range(n):
            pg.evaluate(f'window.goto({f})')
            pg.wait_for_timeout(12)
            raw.append(pg.evaluate(JS))
        b.close()
    os.remove(page_path)

    def tr(r):  return r['m'][4], r['m'][5]
    def rot(r): return math.degrees(math.atan2(r['m'][1], r['m'][0]))

    bx = sum(tr(r['body new'])[0] for r in raw) / len(raw)
    by = sum(tr(r['body new'])[1] for r in raw) / len(raw)
    curves = []
    for f, r in enumerate(raw):
        px, py = tr(r['body new'])
        ex, ey = tr(r['eyes'])
        sx, sy = tr(r['leaf 2'])
        curves.append(dict(
            f=f,
            bdx=round(px - bx, 2), bdy=round(py - by, 2), brot=round(rot(r['body new']), 2),
            hdx=round(ex - px, 2), hdy=round(ey - py, 2),
            sweep=round(rot(r['l hand']), 2),     # the arm that sweeps up and back down
            hold=round(rot(r['r hand']), 2),      # the arm held up, pointing
            sdx=round(sx - px, 2), sdy=round(sy - py, 2),
            shadows=[k for k, v in r.items() if k.startswith('Shape Layer') and not v['hidden']],
        ))
    json.dump(curves, open(os.path.join(HERE, 'ref_curves.json'), 'w'), indent=0)
    print(f'wrote ref_curves.json, {len(curves)} frames')


if __name__ == '__main__':
    main()
