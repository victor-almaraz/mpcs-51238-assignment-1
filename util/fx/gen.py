import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import sys, os; sys.path.insert(0, sys.argv[1]); from mn import *
OUT=REPO + '/v20/assets/pics'
os.makedirs(OUT, exist_ok=True)
m.cmd('WebDriver:Navigate',{'url':'http://localhost:8000/v20/index.html?g=%f'%time.time()})
time.sleep(3)
print(js("return devicePixelRatio"))
js("""Desk.act('close-all'); document.querySelectorAll('.win').forEach(function(w){ if(w.querySelector('canvas[data-pic], canvas[data-drawing], canvas[data-numeral]')) Desk.open(w.id,{focus:false}); });""")
time.sleep(5)
items=js("""var out=[]; document.querySelectorAll('canvas[data-pic], canvas[data-drawing], canvas[data-numeral]').forEach(function(c){
  var key = c.dataset.pic!=null ? (c.dataset.pic==='hero'?'hero':'plate-'+c.dataset.pic) : c.dataset.drawing!=null ? 'drawing-'+c.dataset.drawing : 'numeral-'+c.dataset.numeral+'-t'+(c.dataset.tone||6)+'-h'+(c.dataset.h||120);
  out.push({key:key, w:c.width, h:c.height, ready:c.dataset.ready||'', url:c.toDataURL('image/png')}); }); return out;""")
seen=set()
for it in items:
    if it['key'] in seen: continue
    seen.add(it['key'])
    open(os.path.join(OUT, it['key']+'.png'),'wb').write(base64.b64decode(it['url'].split(',',1)[1]))
    print(it['key'], it['w'], it['h'], it['ready'])
