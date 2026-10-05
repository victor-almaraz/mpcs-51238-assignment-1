import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import numpy as np
from PIL import Image
src = Image.open(REPO + '/v15/assets/misc-persepolis.jpeg').convert('RGB')
W = 960; H = round(856*W/1200)
a = np.asarray(src.resize((W, H), Image.LANCZOS), dtype=np.float64)/255
# hatch matrix, as pixels.js
B=[[0]]
while len(B)<8:
    n=len(B); nx=[[4*B[y%n][x%n]+[0,2,3,1][(2 if y>=n else 0)+(1 if x>=n else 0)] for x in range(2*n)] for y in range(2*n)]; B=nx
STEPS=[lambda x,y:(x+y)%8==0,lambda x,y:(x+y)%8==4,lambda x,y:(x-y+8)%4==0,lambda x,y:y%4==0,lambda x,y:x%4==0]
def stepOf(x,y):
    for s,f in enumerate(STEPS):
        if f(x,y): return s
    return 5
order=sorted([(stepOf(x,y),B[y][x],x,y) for y in range(8) for x in range(8)])
counts=[0]+[sum(1 for p in order if p[0]<=s) for s in range(5)]+[64]
TONES=[1-c/64 for c in counts]
TH=np.zeros((8,8))
for s,b,x,y in order: TH[y,x]=(TONES[s]+TONES[s+1])/2
T=np.tile(TH,(H//8+1,W//8+1))[:H,:W]
def hatch(img): return (img>T[...,None] if img.ndim==3 else img>T)
def atk(g):
    g=g.copy(); h,w=g.shape; out=np.zeros_like(g,dtype=bool)
    for y in range(h):
        for x in range(w):
            o=g[y,x]>=0.5; out[y,x]=o; e=(g[y,x]-o)/8
            for dx,dy in ((1,0),(2,0),(-1,1),(0,1),(1,1),(0,2)):
                X,Y=x+dx,y+dy
                if 0<=X<w and Y<h: g[Y,X]+=e
    return out
np.save('a.npy',a)
np.save('T.npy',T)
lum=a@[0.299,0.587,0.114]
def save(name,rgb): Image.fromarray((rgb*255).astype(np.uint8)).save(name)
# 1 night, 8 colours hatched
save('h8.png',hatch(np.clip(a*1.4,0,1)).astype(float))
# 2 inverted, blue on white, hatched
inv=np.clip((1-lum)*1.0,0,1)
g=hatch(inv); save('hinv.png',np.dstack([g,g,np.ones_like(g)]).astype(float))
# 3 atkinson mono night
k=atk(np.clip(lum*1.6,0,1)); save('atk.png',np.dstack([k,k,k]).astype(float))
# 4 atkinson inverted blue
k=atk(np.clip(1-lum*1.3,0,1)); save('atkinv.png',np.dstack([k,k,np.ones_like(k)]).astype(float))
