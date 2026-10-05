import zlib,struct,sys
d=open(sys.argv[1],'rb').read(); p=8; idat=b''; pal=None
while p<len(d):
    l,=struct.unpack('>I',d[p:p+4]); t=d[p+4:p+8]; c=d[p+8:p+8+l]; p+=12+l
    if t==b'IHDR': w,h,bd,ct,_,_,il=struct.unpack('>IIBBBBB',c)
    elif t==b'PLTE': pal=[tuple(c[i:i+3]) for i in range(0,len(c),3)]
    elif t==b'IDAT': idat+=c
raw=zlib.decompress(idat); stride=w; rows=[]; prev=bytearray(stride); i=0
for y in range(h):
    f=raw[i]; line=bytearray(raw[i+1:i+1+stride]); i+=1+stride
    for x in range(stride):
        a=line[x-1] if x>0 else 0; b=prev[x]; c=prev[x-1] if x>0 else 0
        if f==1: line[x]=(line[x]+a)&255
        elif f==2: line[x]=(line[x]+b)&255
        elif f==3: line[x]=(line[x]+(a+b)//2)&255
        elif f==4:
            pp=a+b-c; pa,pb,pc=abs(pp-a),abs(pp-b),abs(pp-c)
            pr=a if pa<=pb and pa<=pc else (b if pb<=pc else c); line[x]=(line[x]+pr)&255
    prev=line; rows.append(list(line))
x0,y0,x1,y1=map(int,sys.argv[2:6])
used={}
chars='.#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
def ch(v):
    col=pal[v]
    if col==(255,255,255): return '.'
    if col==(0,0,0): return '#'
    if col not in used: used[col]=chars[2+len(used)]
    return used[col]
for y in range(y0,y1): print('%3d '%y+''.join(ch(rows[y][x]) for x in range(x0,x1)))
for k,v in used.items(): print(v,k)
