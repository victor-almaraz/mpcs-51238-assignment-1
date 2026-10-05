import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
from PIL import Image
A=REPO + '/v19/assets/'
sh=Image.open(A+'shelf.webp'); S=5; TOP=32
bg=Image.new('RGBA',(sh.width+40,sh.height+40),(236,232,223,255))
bg.alpha_composite(sh,(20,20))
x=40
for i,w in ((1,32),(2,29),(3,30.5)):
    v=Image.open(A+'vol-%d.webp'%i); bg.alpha_composite(v,(20+int(x*S),20+int((TOP+96)*S)-v.height)); x+=w+1.2
bg.save('cs_shelf.png')
