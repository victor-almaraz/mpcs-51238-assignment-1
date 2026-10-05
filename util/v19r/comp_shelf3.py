import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
from PIL import Image, ImageDraw
A=REPO + '/v21/assets/'
S=6; TOP=32
sh=Image.open(A+'shelf.webp')
bg=Image.new('RGBA',(sh.width+40,sh.height+40),(86,118,143,255)); bg.alpha_composite(sh,(20,20))
def put(im,xu,bottom_u=96):
    bg.alpha_composite(im,(20+int(xu*S),20+int((TOP+bottom_u)*S)-im.height))
x=26
for i,w in ((1,32),(2,29),(3,30.5)):
    put(Image.open(A+'vol-%d.webp'%i),x); x+=w+1.2
put(Image.open(A+'mag-back.webp'),134)
cov=Image.new('RGBA',(62*S,83*S),(13,13,13,255)); d=ImageDraw.Draw(cov); d.rectangle([0,35*S,62*S,83*S],fill=(255,90,31,255))
put(cov,141,94)
put(Image.open(A+'mag-front.webp'),134)
put(Image.open(A+'file-box.webp'),218)
put(Image.open(A+'deck-box.webp'),274)
bg=bg.resize((bg.width//2,bg.height//2)); bg.save('cs_shelf3.png')
