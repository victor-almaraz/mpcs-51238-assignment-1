import math
# busy beaver
tape=[0]*24; h=11; s=1
T={1:[(1,1,2),(1,1,0)],2:[(0,1,3),(1,1,2)],3:[(1,-1,3),(1,-1,1)]}
n=0
while s!=0:
    w,m,nx=T[s][tape[h]]; tape[h]=w; h+=m; s=nx; n+=1
print("BB",n,sum(tape),''.join(map(str,tape)))
T4={1:[(1,1,2),(1,-1,2)],2:[(1,-1,1),(0,-1,3)],3:[(1,1,0),(1,-1,4)],4:[(1,1,4),(0,1,1)]}
tape=[0]*24; h=15; s=1;n=0
while s!=0 and n<200 and 0<=h<24:
    w,m,nx=T4[s][tape[h]]; tape[h]=w; h+=m; s=nx; n+=1
print("BB4",n,sum(tape),h)
# euclid
m,nn=1071,462;steps=0
while nn: m,nn=nn,m%nn;steps+=1
print("gcd",m,steps)
# collatz
x=27;k=0;mx=27
while x>1:
    x= x//2 if x%2==0 else 3*x+1;k+=1;mx=max(mx,x)
print("collatz",k,mx)
# corridor
NR,C,r=997,7,1;seen={};i=0
while True:
    i+=1
    if r in seen: print("corridor step",i,"room",r,"tail",seen[r]-1,"loop",i-seen[r]);break
    seen[r]=i; r=(r*r+C)%NR
# echo
a=1
for k in range(1,15):
    a*=0.75; L=min(9,int(a*9+0.5)); print("echo",k,round(a,4),round(20*math.log10(a),1),L)
# rng
def rnd(ix): return (171*ix)%30269
# tzara
words="THE CARD READER SWALLOWED A DECK OF FORTY HOLES AND THE PRINTER ANSWERED IN CAPITALS NOBODY".split()
ix=191;iw=list(range(1,17))
for L in range(1,16):
    K=17-L; ix=rnd(ix); J=ix%K+1; iw[K-1],iw[J-1]=iw[J-1],iw[K-1]
out=[]
for K in range(16):
    out.append(words[iw[K]-1]); ix=rnd(ix)
    if ix%4==0: out.append('/')
print("tzara",' '.join(out))
# erratum
ix=1913
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
for iv in range(3):
    note=[52+k for k in range(1,26)]
    for L in range(1,25):
        K=26-L; ix=rnd(ix); J=ix%K+1; note[K-1],note[J-1]=note[J-1],note[K-1]
    print("voice",iv+1,' '.join(names[n%12]+str(n//12-1) for n in note))
# stoppages
ix=1914;TURN=0.35
for it in range(3):
    x=y=0; ix=rnd(ix); A=(ix/30269-0.5)*TURN
    for k in range(20):
        ix=rnd(ix); A+=(2*ix/30269-1)*TURN; x+=5*math.cos(A); y+=5*math.sin(A)
    print("thread",it+1,round(math.hypot(x,y),2))
# sitting
ix=1969;X=[]
for k in range(40):
    ix=rnd(ix); X.append(float(ix%10))
LP=[-1]*40
for ig in range(40):
    mn,mxx=min(X),max(X); X=[9*(v-mn)/(mxx-mn) for v in X]; L=[int(v+0.5) for v in X]
    if L==LP: print("sitting stopped at take",ig);break
    print("take",ig,''.join(map(str,L))); LP=L
    for r in range(6):
        X=[0.25*X[k-1]+0.5*X[k]+0.25*X[(k+1)%40] for k in range(40)]
else: print("sitting ran all 40")
# erosion
ix=808;H=[]
for k in range(1,61):
    ix=rnd(ix); H.append(9-abs(k-30)//7-ix%2)
iy=0
for ir in range(16):
    mass=sum(H); print("eros",iy,''.join(map(str,H)),mass)
    if mass==0: print("gone",iy);break
    for y in range(5):
        iy+=1
        for k in range(60):
            if H[k]==0: continue
            ne=0
            if k==0: ne+=1
            if k==59: ne+=1
            if k>0 and H[k-1]<H[k]: ne+=1
            if k<59 and H[k+1]<H[k]: ne+=1
            ix=rnd(ix)
            if ix%100<4+18*ne: H[k]-=1
