import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
from PIL import Image
import os, sys
from build import KINDS, POS, THINGS
R=REPO + '/v25/assets/'
def comp(t, s='task', paper='ogee'):
    O=R+t+'/'
    pr=Image.new('RGBA',(640,320))
    pr.alpha_composite(Image.open(O+'lit/%s/room-%s.png'%(s,paper)).convert('RGBA'),(0,0))
    pr.alpha_composite(Image.open(O+'room-%s-r.png'%paper).convert('RGBA'),(368,0))
    def get(n):
        p=O+'lit/%s/%s'%(s,n)
        return Image.open(p if os.path.exists(p) else O+n).convert('RGBA')
    for k,names in KINDS.items():
        n = names[0] if k!='lamp' else 'lamp-'+(s if s!='off' else 'task')
        pr.alpha_composite(get(n+'.png'),POS[k])
    for n,xy in THINGS.items():
        if n!='px-mag-front.png': pr.alpha_composite(get(n),xy)
    pr.alpha_composite(get('switch-on.png' if s!='off' else 'switch-off.png'),(40,128))
    return pr
s=Image.new('RGB',(1280,640))
for i,t in enumerate(('morning','evening','night')):
    s.paste(comp(t).convert('RGB'),((i%2)*640,(i//2)*320))
s.paste(comp('night','off').convert('RGB'),(640,320))
s.save('times.png')
