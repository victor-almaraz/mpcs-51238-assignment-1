import zlib,struct,sys
def load(fn):
    d=open(fn,'rb').read(); p=8; idat=b''; pal=None
    while p<len(d):
        l,=struct.unpack('>I',d[p:p+4]); t=d[p+4:p+8]; c=d[p+8:p+8+l]; p+=12+l
        if t==b'IHDR': w,h,bd,ct,_,_,il=struct.unpack('>IIBBBBB',c)
        elif t==b'PLTE': pal=[c[i:i+3] for i in range(0,len(c),3)]
        elif t==b'IDAT': idat+=c
    raw=zlib.decompress(idat); assert bd==1 and il==0
    stride=(w+7)//8; rows=[]; prev=bytearray(stride); i=0
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
        prev=line
        rows.append([ (line[x//8]>>(7-x%8))&1 for x in range(w)])
    black=[i for i,c in enumerate(pal) if sum(c)<300]
    return [[1 if v in black else 0 for v in r] for r in rows]
img=load(sys.argv[1])
x0,y0,x1,y1=map(int,sys.argv[2:6])
for y in range(y0,y1):
    print('%3d '%y+''.join('#' if img[y][x] else '.' for x in range(x0,x1)))
