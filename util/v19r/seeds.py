# Clean seeds of v21's room drawings for v23's pixel art: the same drawings, rendered without
# the grain and print-speckle filters (their noise would come through as stray pixels) and
# kept losslessly, into the scratchpad's seeds/ (v21's own assets are not touched).
import os, sys, importlib
import render as R
SEEDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seeds')
os.makedirs(SEEDS, exist_ok=True)
def ident(id_, *a, **k): return '<filter id="%s"><feMerge><feMergeNode in="SourceGraphic"/></feMerge></filter>' % id_
def png_render(name, body, w, h, scale, outdir, fmt='webp', q=90, defs=''):
    return R.render(name, body, w, h, scale, SEEDS, fmt='png', defs=defs)
def load(modname):
    m = importlib.import_module(modname)
    m.OUT = SEEDS; m.print_filter = ident; m.grain_filter = ident; m.render = png_render
    return m
jobs = {'shelf3': ['vols', 'mag_ledge', 'file_box'], 'desk2': ['lamp', 'mug', 'coding_form', 'out_tray', 'deck_box', 'stool'],
        'plants2': ['fig', 'monstera', 'pothos'], 'tape2': ['room'], 'comp2': ['room'], 'station2': ['parts']}
for mod, fns in jobs.items():
    m = load(mod)
    for fn in fns:
        if fn == 'vols':
            for v in m.VOLS: m.volume(v)
        else: getattr(m, fn)()
# the shelf without its print (v22's), for the board and ladders
s4 = load('shelf4'); s4.shelf_bare()
