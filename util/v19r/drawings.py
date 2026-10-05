# v19's miscellanea drawings (inline SVG held in drawings.js) rendered once at 2x, for v21.
import re, json
from render import render, REPO
SRC = REPO + '/v21/drawings.js'
OUT = REPO + '/v21/assets/drawings'
s = open(SRC).read()
D = json.loads(re.sub(r'^\s*(\w+):', r'"\1":', s[s.index('{'):s.rindex('}') + 1], flags=re.M))
meta = {}
for k, svg in D.items():
    vb = [float(v) for v in re.search(r'viewBox="([^"]*)"', svg).group(1).split()]
    w, h = vb[2], vb[3]
    inner = svg[svg.index('>') + 1:svg.rindex('</svg>')]
    render(k, inner, w, h, 2, OUT, q=88)
    meta[k] = dict(w=int(w), h=int(h), alt=re.search(r'aria-label="([^"]*)"', svg).group(1), cls=re.search(r'class="([^"]*)"', svg).group(1))
json.dump(meta, open('drawings_meta.json', 'w'), indent=1)
