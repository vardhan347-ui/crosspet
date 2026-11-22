import numpy as np, trimesh
from manifold3d import Manifold, CrossSection, set_circular_segments
set_circular_segments(96)

def petal_star(R, n, w, hub, rot=0.0):
    polys=[]
    for k in range(n):
        a=rot+2*np.pi*k/n
        ts=np.linspace(0,1,40)
        right=[(R*t, w*(t**0.55*(1-t)**0.45)/(0.55**0.55*0.45**0.45)) for t in ts]
        left=[(x,-y) for x,y in right[::-1]]
        pts=np.array((right+left[1:-1])[::-1])
        c,s=np.cos(a),np.sin(a)
        pts=pts@np.array([[c,s],[-s,c]])
        polys.append(CrossSection([pts.tolist()]))
    cs=CrossSection.circle(hub)
    for p in polys: cs=cs+p
    return cs

def flare(cs, z0, h, s_bot):
    return Manifold.extrude(cs.scale((s_bot,s_bot)), h, 30, 0, (1/s_bot,1/s_bot)).translate((0,0,z0))

# foot
foot=Manifold.cylinder(3, 33, 34).translate((0,0,0))
# lotus: outer petals (offset 22.5deg), inner petals (aligned with spout)
outer=flare(petal_star(46,8,15,25,rot=np.pi/8),3,14,0.72)
inner=flare(petal_star(40,8,13,21.3,rot=0),3,21,0.60)
# diya bowl: teardrop with spout toward +x
bowl_cs=(CrossSection.circle(23)+CrossSection.circle(3.5).translate((37,0))).hull()
bowl=flare(bowl_cs,8,24,0.86)
body=foot+outer+inner+bowl
# tealight recess (standard tealight ~38-39mm)
TOP=32
body=body-Manifold.cylinder(15,20.25,20.25).translate((0,0,TOP-14))
# wick groove along spout
groove=Manifold.cube((14,2.4,2.5)).translate((20.5,-1.2,TOP-1.5))
body=body-groove
# flame on spout tip: revolved teardrop profile (support-free)
zs=np.linspace(0,15,60)
r=np.where(zs<4.5, 2.0+2.2*np.sin(zs/4.5*np.pi/2), 4.2*np.cos((zs-4.5)/10.5*np.pi/2)**1.3)
prof=[(0,-0.5),(2.0,-0.5)]+[(rr,z) for rr,z in zip(r[:-1],zs[:-1])]+[(0,15)]
flame=Manifold.revolve(CrossSection([prof]),64).translate((37,0,TOP))
body=body+flame
print("status",body.status()); m=body.to_mesh()
mesh=trimesh.Trimesh(m.vert_properties[:,:3], m.tri_verts); mesh.merge_vertices()
print("watertight",mesh.is_watertight,"extents",mesh.extents.round(1),"vol cm3",round(mesh.volume/1000,1))
mesh.export("diwali_lotus_diya.stl")
