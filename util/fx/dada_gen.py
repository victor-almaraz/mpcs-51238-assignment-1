# Offline port of v20/dada.js's two chance pictures, through the same hatch matrix as pixels.js
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random, json
import numpy as np
from PIL import Image
OUT=REPO + '/v20/assets/pics/'
B=[[0]]
while len(B)<8:
    n=len(B); B=[[4*B[y%n][x%n]+[0,2,3,1][(2 if y>=n else 0)+(1 if x>=n else 0)] for x in range(2*n)] for y in range(2*n)]
STEPS=[lambda x,y:(x+y)%8==0,lambda x,y:(x+y)%8==4,lambda x,y:(x-y+8)%4==0,lambda x,y:y%4==0,lambda x,y:x%4==0]
def stepOf(x,y):
    for s,f in enumerate(STEPS):
        if f(x,y): return s
    return 5
order=sorted([(stepOf(x,y),B[y][x],x,y) for y in range(8) for x in range(8)])
counts=[0]+[sum(1 for p in order if p[0]<=s) for s in range(5)]+[64]
TONES=[1-c/64 for c in counts]
TH=[[0]*8 for _ in range(8)]
for s,b,x,y in order: TH[y][x]=(TONES[s]+TONES[s+1])/2
def rgbBits(c,x,y):
    t=TH[y&7][x&7]; return tuple(255 if v>t else 0 for v in c)
BLACK=(0,0,0); WHITE=(255,255,255)
class S:
    def __init__(s,W,H): s.W=W; s.H=H; s.a=np.zeros((H,W,4),np.uint8)
    def set(s,x,y,p):
        x=int(math.floor(x+0.5)); y=int(math.floor(y+0.5))
        if x<0 or y<0 or x>=s.W or y>=s.H: return
        s.a[y,x,:3]=p; s.a[y,x,3]=255
    def hatch(s,x,y,t): s.set(x,y,rgbBits(t,x,y))
    def rect(s,x0,y0,w,h,fn):
        for y in range(y0,y0+h):
            for x in range(x0,x0+w): fn(x,y)
    def save(s,f): Image.fromarray(s.a).save(f, optimize=True)
M=240; X0=20
def thread(mid, rnd):
    a0=(rnd.random()-0.5)*0.3
    waves=[{'f':1+rnd.random()*2.2,'p':rnd.random()*2*math.pi,'A':0.15+rnd.random()*0.35} for _ in range(3)]
    soft=1.0
    while True:
        pts=[]; x=X0; y=mid; ok=True
        for i in range(M+1):
            pts.append((x,y))
            a=a0*soft
            for v in waves: a+=soft*v['A']*math.sin(2*math.pi*v['f']*i/M+v['p'])
            x+=math.cos(a); y+=math.sin(a)
            if abs(y-mid)>20: ok=False
        if ok or soft<0.05: return pts
        soft*=0.8
def stoppages(k):
    rnd=random.Random(1913+k*7)
    W,H=300,194; s=S(W,H); spans=[]
    s.rect(0,0,W,H,lambda x,y:s.set(x,y,WHITE))
    for x in range(X0,X0+M+1): s.set(x,8,BLACK)
    for t in range(11):
        for j in range(5 if t%5 else 3,8): s.set(X0+24*t,j,BLACK)
    for y0 in (22,80,138):
        mid=y0+24
        s.rect(10,y0,W-20,48,lambda x,y:s.hatch(x,y,(0.45,0.45,0.85)))
        s.rect(10,y0,W-20,1,lambda x,y:s.set(x,y,BLACK)); s.rect(10,y0+47,W-20,1,lambda x,y:s.set(x,y,BLACK))
        s.rect(10,y0,1,48,lambda x,y:s.set(x,y,BLACK)); s.rect(W-11,y0,1,48,lambda x,y:s.set(x,y,BLACK))
        pts=thread(mid,rnd)
        for p in pts:
            for dy in (-1,0,1):
                for dx in (-1,0,1): s.set(p[0]+dx,p[1]+dy,WHITE)
        for p in pts: s.set(p[0],p[1],BLACK)
        end=pts[-1]; span=math.sqrt((end[0]-X0)**2+(end[1]-mid)**2)/M
        for x in range(X0,X0+M+1):
            if x<=X0+span*M or x%2==0: s.set(x,y0+52,BLACK)
        spans.append(round(span,2))
    s.save(OUT+'dada-stoppages-%d.png'%k); return spans
def h(i):
    v=math.sin(i*127.1+311.7)*43758.5453; return v-math.floor(v)
def squares(k):
    rnd=random.Random(1916+k*13)
    W,H=280,200; s=S(W,H); seed=rnd.random()*1000
    s.rect(0,0,W,H,lambda x,y:s.hatch(x,y,(1,1,0.82)))
    FILLS=[(BLACK,True),((0.5,0.5,0.5),False),((0.35,0.35,0.8),False),((1,1,1),False),((0.62,0.62,0.62),False)]
    n=12+int(rnd.random()*6)
    for i in range(n):
        w=2*(8+int(rnd.random()*14)); hh=w if rnd.random()<0.6 else 2*(8+int(rnd.random()*14))
        x0=14+int(rnd.random()*(W-28-w)); y0=12+int(rnd.random()*(H-24-hh))
        f=FILLS[int(rnd.random()*len(FILLS))]; kk=seed+i*17
        for y in range(y0,y0+hh):
            for x in range(x0,x0+w):
                l=x0+int(h(kk+y)*2.4); r=x0+w-1-int(h(kk+50+y)*2.4)
                tp=y0+int(h(kk+100+x)*2.4); bt=y0+hh-1-int(h(kk+150+x)*2.4)
                if x<l or x>r or y<tp or y>bt: continue
                edge=x in (l,r) or y in (tp,bt)
                if f[1] or edge: s.set(x,y,BLACK)
                else: s.hatch(x,y,f[0])
    s.save(OUT+'dada-arp-%d.png'%k)
meta={'stoppages':[stoppages(k) for k in range(1,9)]}
for k in range(1,9): squares(k)
print(json.dumps(meta))
