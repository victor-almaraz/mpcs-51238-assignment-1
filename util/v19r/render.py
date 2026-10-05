# Render SVG drawings to images through headless Chrome (a scratch profile, killed after
# each shot), then save them as WebP (or PNG) for v19/assets/.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import base64, os, subprocess, time, glob, signal
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = REPO
FONTS = REPO + '/fonts/'
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PROF = HERE + '/chrome-prof'

FACES = [('Work Sans', 400, 'work-sans/work-sans-latin-400-normal.woff2'),
         ('Work Sans', 600, 'work-sans/work-sans-latin-600-normal.woff2'),
         ('Jost', 400, 'jost/jost-latin-400-normal.woff2'),
         ('Jost', 600, 'jost/jost-latin-600-normal.woff2'),
         ('Arvo', 700, 'arvo/arvo-latin-700-normal.woff2'),
         ('Courier Prime', 400, 'courier-prime/courier-prime-latin-400-normal.woff2'),
         ('Courier Prime', 700, 'courier-prime/courier-prime-latin-700-normal.woff2'),
         ('Caveat', 400, 'caveat/caveat-latin-400-normal.woff2'),
         ('Caveat', 700, 'caveat/caveat-latin-700-normal.woff2'),
         ('Old Standard TT', 400, 'old-standard-tt/old-standard-tt-latin-400-normal.woff2'),
         ('Old Standard TT', 700, 'old-standard-tt/old-standard-tt-latin-700-normal.woff2'),
         ('Archivo Black', 400, 'archivo-black/archivo-black-latin-400-normal.woff2'),
         ('Bodoni Moda', 400, 'bodoni-moda/bodoni-moda-latin-400-normal.woff2'),
         ('Bodoni Moda', 700, 'bodoni-moda/bodoni-moda-latin-700-normal.woff2'),
         ('Big Shoulders Display', 800, 'big-shoulders-display/big-shoulders-display-latin-800-normal.woff2'),
         ('Oswald', 600, 'oswald/oswald-latin-600-normal.woff2')]
FACES_ITALIC = [('Bodoni Moda', 400, 'bodoni-moda/bodoni-moda-latin-400-italic.woff2')]
_css = None
def font_css():
    global _css
    if _css is None:
        _css = ''.join('@font-face{font-family:"%s";font-weight:%d;src:url(data:font/woff2;base64,%s) format("woff2")}'
                       % (f, w, base64.b64encode(open(FONTS + p, 'rb').read()).decode()) for f, w, p in FACES)
        _css += ''.join('@font-face{font-family:"%s";font-weight:%d;font-style:italic;src:url(data:font/woff2;base64,%s) format("woff2")}'
                        % (f, w, base64.b64encode(open(FONTS + p, 'rb').read()).decode()) for f, w, p in FACES_ITALIC)
    return _css

def render(name, body, w, h, scale, outdir, fmt='webp', q=90, defs=''):
    """body: SVG markup in user units, w×h units, drawn at `scale` px per unit."""
    W, H = int(round(w * scale)), int(round(h * scale))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %g %g">'
           '<defs>%s</defs>%s</svg>') % (W, H, w, h, defs, body)
    os.makedirs(HERE + '/svg', exist_ok=True)
    open(HERE + '/svg/%s.svg' % name, 'w', encoding='utf-8').write(svg)
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>%s html,body{margin:0;background:transparent;overflow:hidden}svg{display:block}</style></head>'
            '<body>%s</body></html>') % (font_css(), svg)
    hp = HERE + '/svg/%s.html' % name
    open(hp, 'w', encoding='utf-8').write(html)
    png = HERE + '/svg/%s.png' % name
    if os.path.exists(png): os.remove(png)
    p = subprocess.Popen([CH, '--headless=new', '--user-data-dir=' + PROF, '--no-first-run', '--disable-gpu',
                          '--hide-scrollbars', '--default-background-color=00000000', '--force-device-scale-factor=1',
                          '--virtual-time-budget=3000', '--window-size=%d,%d' % (W, H), '--screenshot=' + png, 'file://' + hp],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    t0 = time.time(); last = -1
    while time.time() - t0 < 60:
        time.sleep(0.4)
        if os.path.exists(png):
            s = os.path.getsize(png)
            if s == last and s > 0: break
            last = s
    try: os.killpg(p.pid, signal.SIGKILL)
    except Exception: pass
    subprocess.run(['pkill', '-9', '-f', 'user-data-dir=' + PROF])
    im = Image.open(png).convert('RGBA')
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, name + '.' + fmt)
    if fmt == 'webp': im.save(out, 'WEBP', quality=q, method=6, alpha_quality=100)
    else: im.save(out, optimize=True)
    print(name, im.size, os.path.getsize(out) // 1024, 'KB')
    return im
