# The Xenakis miscellanea's drawings (v19's drawings.js, inline SVG strings) cleaned up into
# SVG files for v21: runs of like lines, rects and circles merged into single paths, the type
# turned to outlines of its own faces (so each file stands alone as an image), numbers
# rounded, classes and ARIA moved to the page's img. Painting order is kept.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import re, json, math, os
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

REPO = REPO
SRC = REPO + '/v21/drawings.js'
OUT = REPO + '/v21/assets/misc'
os.makedirs(OUT, exist_ok=True)
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
FONTS = {}
def font(family, weight):
    fam = family.split(',')[0].strip().strip('"')
    key = (fam, 700 if str(weight) in ('700', 'bold') else 400)
    if key not in FONTS:
        slug = fam.lower().replace(' ', '-')
        FONTS[key] = TTFont('%s/fonts/%s/%s-latin-%d-normal.woff2' % (REPO, slug, slug, key[1]))
    t = FONTS[key]
    return t.getGlyphSet(), t.getBestCmap(), t['head'].unitsPerEm, t['hmtx']

def n(v):
    v = float(v)
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

GEOM = {'line': ('x1', 'y1', 'x2', 'y2'), 'rect': ('x', 'y', 'width', 'height'), 'circle': ('cx', 'cy', 'r')}
def style_key(el):
    return tuple(sorted((k, v) for k, v in el.attrib.items() if k not in GEOM.get(el.tag.split('}')[1], ())))

def to_d(el):
    t = el.tag.split('}')[1]; a = el.attrib
    if t == 'line': return 'M%s %sL%s %s' % (n(a['x1']), n(a['y1']), n(a['x2']), n(a['y2']))
    if t == 'rect':
        x, y, w, h = (float(a.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
        return 'M%s %sh%sv%sh%sz' % (n(x), n(y), n(w), n(h), n(-w))
    if t == 'circle':
        cx, cy, r = float(a['cx']), float(a['cy']), float(a['r'])
        return 'M%s %sa%s %s 0 1 0 %s 0a%s %s 0 1 0 %s 0z' % (n(cx - r), n(cy), n(r), n(r), n(2 * r), n(r), n(r), n(-2 * r))

GLYPHS = {}   # (font key, glyph name) -> id, defined once per file in <defs>
def glyph_id(fkey, gn, gs):
    k = (fkey, gn)
    if k not in GLYPHS:
        gid = 'g%d' % len(GLYPHS)
        pen = SVGPathPen(gs, ntos=lambda v: str(int(round(v))))
        gs[gn].draw(pen)
        GLYPHS[k] = (gid, pen.getCommands())
    return GLYPHS[k][0]

def text_path(el):
    """the text as glyphs, each glyph's outline defined once in the file and used again"""
    a = el.attrib
    s = ''.join(el.itertext())
    size = float(a.get('font-size', 16))
    fam, wt = a.get('font-family', 'Courier Prime'), a.get('font-weight', 400)
    gs, cmap, upm, hmtx = font(fam, wt)
    fkey = (fam.split(',')[0], str(wt))
    ls = float(a.get('letter-spacing', 0)) * upm / size
    width = sum(hmtx[cmap.get(ord(c), cmap[ord('?')])][0] + ls for c in s) - (ls if s else 0)
    x, y = float(a.get('x', 0)), float(a.get('y', 0))
    sc = size / upm
    anchor = a.get('text-anchor', 'start')
    if anchor == 'middle': x -= width * sc / 2
    elif anchor == 'end': x -= width * sc
    grp = ET.Element('{%s}g' % NS)
    tr = 'translate(%s %s) scale(%s %s)' % (n(x), n(y), ('%.5f' % sc).rstrip('0'), ('%.5f' % -sc).rstrip('0'))
    if 'transform' in a: tr = a['transform'] + ' ' + tr
    grp.set('transform', tr)
    for k in ('fill', 'opacity', 'fill-opacity'):
        if k in a: grp.set(k, a[k])
    if 'fill' not in a: grp.set('fill', '#000')
    u = 0.0
    for c in s:
        gn = cmap.get(ord(c), cmap[ord('?')])
        if c != ' ':
            use = ET.SubElement(grp, '{%s}use' % NS)
            use.set('href', '#' + glyph_id(fkey, gn, gs))
            if u: use.set('x', str(int(round(u))))
        u += hmtx[gn][0] + ls
    return grp

def clean(el):
    kids = list(el)
    for k in kids: el.remove(k)
    out, run, rkey = [], [], None
    def flush():
        nonlocal run, rkey
        if not run: return
        if len(run) == 1: out.append(run[0])
        else:
            p = ET.Element('{%s}path' % NS)
            for k, v in rkey[1]: p.set(k, v)
            p.set('d', ''.join(to_d(e) for e in run))
            if run[0].tag.endswith('line') and 'fill' not in dict(rkey[1]): p.set('fill', 'none')
            out.append(p)
        run, rkey = [], None
    for k in kids:
        t = k.tag.split('}')[1]
        if t == 'text': k = text_path(k); t = 'g'
        elif t in ('g', 'defs', 'pattern', 'clipPath', 'mask'): clean(k)
        if t in GEOM and not (t == 'rect' and ('rx' in k.attrib or 'ry' in k.attrib)):
            key = (t, style_key(k))
            if key != rkey: flush(); rkey = key
            run.append(k)
        else:
            flush(); out.append(k)
    flush()
    for k in out:
        for at in list(k.attrib):
            if at in ('x', 'y', 'width', 'height', 'cx', 'cy', 'r', 'x1', 'y1', 'x2', 'y2', 'stroke-width') and re.fullmatch(r'-?[\d.]+', k.attrib[at]):
                k.set(at, n(k.attrib[at]))
        el.append(k)

def main():
    s = open(SRC).read()
    D = json.loads(re.sub(r'^\s*(\w+):', r'"\1":', s[s.index('{'):s.rindex('}') + 1], flags=re.M))
    meta = {}
    for key, src in D.items():
        # some tags carry an attribute twice (the browser keeps the first); keep the first
        def dedupe(m):
            seen = set(); out = []
            for am in re.finditer(r'\s([\w:-]+)="[^"]*"', m.group(2)):
                if am.group(1) in seen: continue
                seen.add(am.group(1)); out.append(am.group(0))
            return '<' + m.group(1) + ''.join(out) + m.group(3) + '>'
        src = re.sub(r'<([\w:]+)((?:\s[\w:-]+="[^"]*")*)\s*(/?)>', dedupe, src)
        GLYPHS.clear()
        root = ET.fromstring(src)
        cls, label = root.get('class', ''), root.get('aria-label', '')
        for at in ('class', 'role', 'aria-label'): root.attrib.pop(at, None)
        vb = [float(v) for v in root.get('viewBox').split()]
        root.set('width', n(vb[2])); root.set('height', n(vb[3]))
        clean(root)
        if GLYPHS:
            defs = ET.Element('{%s}defs' % NS)
            for gid, d in GLYPHS.values():
                p = ET.SubElement(defs, '{%s}path' % NS); p.set('id', gid); p.set('d', d)
            root.insert(0, defs)
        title = ET.Element('{%s}title' % NS); title.text = label
        root.insert(0, title)
        data = ET.tostring(root, encoding='unicode')
        open(os.path.join(OUT, key + '.svg'), 'w').write(data)
        meta[key] = dict(w=int(vb[2]), h=int(vb[3]), alt=label, cls=cls)
        print(key, len(src), '->', len(data))
    json.dump(meta, open(os.path.join(os.path.dirname(__file__), 'misc_meta.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
