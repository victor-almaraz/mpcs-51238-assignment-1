import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import numpy as np
from PIL import Image
src = Image.open(REPO + '/v15/assets/misc-persepolis.jpeg').convert('RGB')
W = 800; H = 570
a = np.asarray(src.resize((W, H), Image.LANCZOS), dtype=np.float64)/255
lum = a@[0.299,0.587,0.114]
# the edges fade into the night, so the picture has no border on a wide screen
yy, xx = np.mgrid[0:H, 0:W]
fx = np.clip(np.minimum(xx, W-1-xx)/(0.08*W), 0, 1); fy = np.clip(np.minimum(yy, H-1-yy)/(0.06*H), 0, 1)
fade = np.sqrt(fx*fy)
lum = lum*fade
def atk(g):
    g=g.copy(); h,w=g.shape; out=np.zeros((h,w),bool)
    for y in range(h):
        row=g[y]
        for x in range(w):
            v=row[x]; o=v>=0.5; out[y,x]=o; e=(v-o)/8
            if x+1<w: row[x+1]+=e
            if x+2<w: row[x+2]+=e
            if y+1<h:
                if x>0: g[y+1,x-1]+=e
                g[y+1,x]+=e
                if x+1<w: g[y+1,x+1]+=e
            if y+2<h: g[y+2,x]+=e
    return out
k = atk(np.clip(lum*1.6, 0, 1))
r,gc,b = a[...,0],a[...,1],a[...,2]
warm = (r > 0.8) & (r - b > 0.3)
green = (gc - r > 0.06) & (gc - b > 0.0) & (gc > 0.25)
out = np.zeros((H,W,3),np.uint8)
out[k] = 255
out[k & warm] = (255,255,0)
out[k & green] = (0,255,0)
im = Image.fromarray(out).convert('P', palette=Image.ADAPTIVE, colors=4)
im.save('night800.png', optimize=True, bits=2)
print(warm.sum(), green.sum())
