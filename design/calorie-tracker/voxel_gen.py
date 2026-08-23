import math, json, os

def hx(c): return '#%02X%02X%02X' % tuple(max(0,min(255,round(v))) for v in c)
def rgb(h):
    h=h.lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))
def shade(h, f):
    r,g,b = rgb(h); return hx((r*f, g*f, b*f))

TOP, RIGHT, LEFT = 1.16, 0.86, 0.64

def cube_paths(cx, cy, base, w, h, d):
    """cx,cy = top vertex of the cube's top face."""
    n = lambda v: round(v,1)
    top   = f'M{n(cx)},{n(cy)} {n(cx+w)},{n(cy+h)} {n(cx)},{n(cy+2*h)} {n(cx-w)},{n(cy+h)}Z'
    left  = f'M{n(cx-w)},{n(cy+h)} {n(cx)},{n(cy+2*h)} {n(cx)},{n(cy+2*h+d)} {n(cx-w)},{n(cy+h+d)}Z'
    right = f'M{n(cx)},{n(cy+2*h)} {n(cx+w)},{n(cy+h)} {n(cx+w)},{n(cy+h+d)} {n(cx)},{n(cy+2*h+d)}Z'
    return [(left,  shade(base, LEFT)),
            (right, shade(base, RIGHT)),
            (top,   shade(base, TOP))]

def render(cells, pal, w=13, h=6.5, d=15, pad=10):
    """cells: list of (x, y, z, key). Returns (svg_body, vb_w, vb_h)."""
    placed = {(x,y,z) for x,y,z,_ in cells}
    vis = [c for c in cells
           if not all(((c[0]+dx, c[1]+dy, c[2]+dz) in placed)
                      for dx,dy,dz in ((1,0,0),(0,1,0),(0,0,1)))]
    vis.sort(key=lambda c: (c[0]+c[2]+c[1]))
    pts=[]
    for x,y,z,k in vis:
        cx = (x - z) * w
        cy = (x + z) * h - y * d
        pts.append((cx,cy))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    minx, maxx = min(xs)-w, max(xs)+w
    miny, maxy = min(ys), max(ys)+2*h+d
    ox, oy = -minx+pad, -miny+pad
    out=[]
    for (x,y,z,k),(cx,cy) in zip(vis, pts):
        for path, col in cube_paths(cx+ox, cy+oy, pal[k], w, h, d):
            out.append(f'<path d="{path}" fill="{col}"/>')
    return ''.join(out), round(maxx-minx+pad*2), round(maxy-miny+pad*2)

# ---- models (grid space) ----
def plate(n, ox=0, oy=0, oz=0, lo=None):
    """Square tray tile, one voxel deep."""
    lo = -n if lo is None else lo
    return [(x+ox, oy-1, z+oz, 'plate')
            for x in range(lo, n+1) for z in range(lo, n+1)]

def bowl(R=2.8, oy=0, ox=0, oz=0, rim='rim', body='bowl', fill='cream'):
    """Hollow: wall runs y=1..3, contents sit at y=2 so you see into it."""
    cells=[]
    for x in range(-3,4):
        for z in range(-3,4):
            dist = math.hypot(x,z)
            if dist <= R-0.8:
                cells.append((x+ox, 0+oy, z+oz, body))
            if R-1.25 < dist <= R:
                for y in (1,2):
                    cells.append((x+ox, y+oy, z+oz, body))
                cells.append((x+ox, 3+oy, z+oz, rim))
            elif dist <= R-1.25:
                cells.append((x+ox, 2+oy, z+oz, fill))
    for tx,tz,k in ((-1,0,'green'), (0,-1,'tomato'), (1,1,'green'), (1,-1,'cream'), (0,1,'green')):
        cells.append((tx+ox, 3+oy, tz+oz, k))
    return cells

def apple(ox=0, oy=0, oz=0, body='apple'):
    cells=[]
    for x in (-1,0,1):
        for z in (-1,0,1):
            for y in (0,1,2):
                if not (abs(x)==1 and abs(z)==1 and y in (0,2)):
                    cells.append((x+ox, y+oy, z+oz, body))
    cells.append((0+ox, 3+oy, 0+oz, 'stem'))
    cells.append((1+ox, 3+oy, 0+oz, 'leaf'))
    return cells

def glass(ox=0, oy=0, oz=0):
    cells=[]
    for y in range(6):
        for x in (0,1):
            for z in (0,1):
                cells.append((x+ox, y+oy, z+oz,
                              'rimglass' if y==5 else ('glass' if y>=4 else 'water')))
    return cells

PAL_A = {'bowl':'#A8467A','rim':'#C86A9C','cream':'#F2E3C8','green':'#A2B876','tomato':'#DE5C46',
         'apple':'#CC4470','stem':'#7A5A46','leaf':'#8FB268','glass':'#C3B6E2','rimglass':'#DCD3F0','water':'#8E71CC','plate':'#B7A6CF'}
PAL_B = {'bowl':'#365DF5','rim':'#6792FF','cream':'#FFF3D8','green':'#C9D48A','tomato':'#FA644C',
         'apple':'#F0553C','stem':'#8A6A4A','leaf':'#C9D48A','glass':'#BCD2FF','rimglass':'#DCE8FF','water':'#6792FF','plate':'#A8BEE2'}

scenes = {}
def R(dx):  return (dx, -dx)      # move right on screen by 2*dx*w

ax, az = R(4)
scenes['a_hero']   = render(plate(3) + bowl() + plate(1,ox=ax,oz=az) + apple(ox=ax,oz=az),
                            PAL_A, w=11, h=5.5, d=13)
gx, gz = R(-4)
scenes['a_detail'] = render(plate(3) + bowl() + plate(1,ox=ax,oz=az) + apple(ox=ax,oz=az)
                            + plate(0,lo=-1,ox=gx,oz=gz) + glass(ox=gx,oz=gz),
                            PAL_A, w=15, h=7.5, d=17)
scenes['b_hero']   = render(plate(3) + bowl() + plate(1,ox=ax,oz=az) + apple(ox=ax,oz=az)
                            + plate(0,lo=-1,ox=gx,oz=gz) + glass(ox=gx,oz=gz),
                            PAL_B, w=13, h=6.5, d=15)
scenes['b_detail'] = render(plate(3) + bowl(), PAL_B, w=20, h=10, d=23)
scenes['thumb_a']  = render(apple(), PAL_A, w=9, h=4.5, d=10, pad=4)
scenes['thumb_b']  = render(apple(), PAL_B, w=9, h=4.5, d=10, pad=4)

out = {k: {'body':v[0], 'w':v[1], 'h':v[2], 'paths':v[0].count('<path')} for k,v in scenes.items()}
json.dump(out, open(os.path.join(os.path.dirname(__file__),'scenes.json'),'w'))
for k,v in out.items():
    print(f"{k}: {v['w']}x{v['h']}  {v['paths']} paths  {len(v['body'])//1024} KB")
