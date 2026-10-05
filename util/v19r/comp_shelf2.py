import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
from PIL import Image, ImageDraw
A=REPO + '/'
S=5; TOP=32; B=(TOP+96)*S
sh=Image.open(A+'v21/assets/shelf.webp')
bg=Image.new('RGBA',(sh.width+40,sh.height+40),(236,232,223,255)); bg.alpha_composite(sh,(20,20))
def put(im,xu,bottom_u=96):
    bg.alpha_composite(im,(20+int(xu*S),20+int((TOP+bottom_u)*S)-im.height))
x=26
for i,w in ((1,32),(2,29),(3,30.5)):
    put(Image.open(A+'v19/assets/vol-%d.webp'%i),x); x+=w+1.2
put(Image.open(A+'v21/assets/mag-back.webp'),134)
cov=Image.new('RGBA',(62*S,83*S),(13,13,13,255)); d=ImageDraw.Draw(cov); d.rectangle([0,35*S,62*S,83*S],fill=(255,90,31,255))
put(cov,141,94)
put(Image.open(A+'v21/assets/mag-front.webp'),134)
put(Image.open(A+'v21/assets/file-box.webp'),218)
put(Image.open(A+'v19/assets/deck-box.webp'),274)
bg.save('cs_shelf2.png')
