# v23's computer pictures, in full colour on the room's palette, at v20's screen sizes (one
# screen pixel is two CSS pixels), so the computer's page keeps its markup: the desk picture
# and the documents' pictures are cut from v22's SVG pictures and v21's engraved plates by
# pix.pixelate; the numerals are set in Pixelify Sans in each sheet's colour; Duchamp's falls
# and Arp's drops are drawn here, pixel by pixel, eight of each.
import io, math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from pix import pixelate, save, HERE, REPO
from room import render_svg, near, rgb

OUT = REPO + '/v23/assets/pics/'
V22 = REPO + '/v22/assets/screen/'
V21M = REPO + '/v21/assets/misc/'

def font(slug, weight=400, size=10):
    t = TTFont('%s/fonts/%s/%s-latin-%d-normal.woff2' % (REPO, slug, slug, weight)) if 'fusion' not in slug else TTFont(_fusion(slug))
    t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0)
    return ImageFont.truetype(b, size)
def _fusion(slug):
    import glob
    return glob.glob('%s/fonts/%s/*.woff2' % (REPO, slug))[0]

def from_svg(src, w, h, name, scale=6, bias=0.15):
    big = render_svg(src, w, h, scale)
    save(pixelate(big, w, h, line_bias=bias), OUT + name)

def pictures():
    from_svg(V22 + 'desktop.svg', 800, 570, 'desktop.png', 4, bias=0)
    from_svg(V22 + 'hero.svg', 292, 100, 'hero.png')
    for k in range(9): from_svg(V22 + 'plate-%d.svg' % k, 322, 56, 'plate-%d.png' % k)
    for d, m, w, h in (('a', 'a1', 280, 180), ('c', 'c1', 280, 160), ('d', 'd1', 220, 165), ('e', 'e1', 300, 150), ('f', 'f1', 280, 160), ('i', 'i1', 320, 165), ('j', 'j1', 320, 172)):
        from_svg(V21M + m + '.svg', w, h, 'drawing-%s.png' % d, bias=0.12)
    from_svg(V22 + 'ball.svg', 240, 200, 'drawing-k.png')
    from_svg(V22 + 'hat.svg', 240, 160, 'drawing-t.png')

TONES = [(74, 104, 134), (224, 205, 176), (216, 189, 146), (201, 154, 46), (168, 119, 83), (116, 62, 43), (61, 43, 32)]
INK = (30, 29, 27)

def numerals():
    # each the size v20's was, the figures set in Pixelify Sans bold without smoothing, filled
    # in the sheet's colour (the About documents' in the room's blue), outlined in ink, with a
    # one-pixel shadow down and to the right
    import glob, os, re
    for p in sorted(glob.glob(REPO + '/v20/assets/pics/numeral-*.png')):
        name = os.path.basename(p)
        m = re.match(r'numeral-(\d+)-t(\d)-h(\d+)\.png', name)
        text, tone = m.group(1), int(m.group(2))
        W, H = Image.open(p).size
        size = H + 8
        f = font('pixelify-sans', 700, size)
        while True:
            l, t, r, b = f.getbbox(text)
            if r - l <= W - 3 and b - t <= H - 3: break
            size -= 1; f = font('pixelify-sans', 700, size)
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        mask = Image.new('L', (W, H), 0)
        dr = ImageDraw.Draw(mask); dr.fontmode = '1'
        dr.text((1 - l, (H - 2 - (b - t)) // 2 - t), text, font=f, fill=255)
        mk = np.array(mask) > 127
        a = np.zeros((H, W, 4), dtype=np.uint8)
        fill = TONES[tone]
        lite = tuple(near(np.clip(np.array(fill) + (255 - np.array(fill)) * 0.3, 0, 255)))
        grown = mk.copy(); grown[1:] |= mk[:-1]; grown[:-1] |= mk[1:]; grown[:, 1:] |= mk[:, :-1]; grown[:, :-1] |= mk[:, 1:]
        sh = np.zeros_like(mk); sh[2:, 2:] = grown[:-2, :-2]
        a[sh & ~grown] = INK + (90,)
        a[grown & ~mk] = INK + (255,)
        a[mk] = fill + (255,)
        top = mk.copy(); top[1:] &= ~mk[:-1]          # the top row of each stroke, lit
        a[top & mk] = lite + (255,)
        save(Image.fromarray(a), OUT + name)

def stoppages():
    # a metre (240 screen pixels) let fall on each of three strips of Prussian blue: the
    # thread's heading wanders as three slow waves of chance; its span ruled and lettered
    f = font('fusion-pixel-10px-proportional-jp', 400, 10)
    spans_all = []
    for n in range(8):
        rnd = random.Random(1913 + n)
        W, H = 300, 194
        im = Image.new('RGB', (W, H), (239, 226, 194))
        dr = ImageDraw.Draw(im); dr.fontmode = '1'
        x0 = 30
        dr.line([(x0, 12), (x0 + 240, 12)], fill=INK)
        for k in range(11): dr.line([(x0 + k * 24, 12), (x0 + k * 24, 12 - (4 if k % 5 == 0 else 2))], fill=INK)
        dr.text((x0 + 246, 5), '1 m', font=f, fill=INK)
        spans = []
        for s in range(3):
            top = 22 + s * 57
            dr.rectangle([14, top, W - 15, top + 38], fill=(43, 69, 96))
            dr.line([(14, top), (W - 15, top)], fill=(74, 104, 134))
            for tries in range(20):
                waves = [((0.75 - k * 0.2) * (rnd.random() * 2 - 1) * 0.88 ** tries, 0.6 + k * 0.9 + rnd.random() * 0.8, rnd.random() * 6.283) for k in range(3)]
                x, y, pts = 0.0, 0.0, [(0.0, 0.0)]
                for i in range(1, 481):
                    t = i / 480; th = sum(a * math.sin(6.283 * fq * t + p) for a, fq, p in waves)
                    x += 0.5 * math.cos(th); y += 0.5 * math.sin(th); pts.append((x, y))
                ys = [p[1] for p in pts]
                if max(ys) - min(ys) < 30: break
            oy = top + 19 - (max(ys) + min(ys)) / 2
            seq = [(int(round(x0 + px_)), int(round(oy + py_))) for px_, py_ in pts]
            for (ax, ay) in seq: im.putpixel((ax + 1, ay + 1), (30, 45, 62))
            for (ax, ay) in seq: im.putpixel((ax, ay), (251, 248, 240))
            ex = seq[-1][0]
            span = math.hypot(pts[-1][0], pts[-1][1]) / 240
            spans.append(round(span, 2))
            by = top + 44
            dr.line([(x0, by), (ex, by)], fill=INK); dr.line([(x0, by - 3), (x0, by + 3)], fill=INK); dr.line([(ex, by - 3), (ex, by + 3)], fill=INK)
            dr.text((ex + 4, by - 6), '%.2f m' % span, font=f, fill=INK)
        save(im, OUT + 'dada-stoppages-%d.png' % (n + 1))
        spans_all.append(spans)
    json.dump(spans_all, open(HERE + '/falls.json', 'w'))
    print(spans_all)

def arp():
    # squares and oblongs of paper, torn, let fall near square on a yellow sheet: ink, grey,
    # the room's blue and paper, each with its torn edge and a one-pixel shadow
    COLS = [INK, INK, INK, (98, 96, 89), (43, 69, 96), (251, 248, 240), (134, 123, 104)]
    for n in range(8):
        rnd = random.Random(1916 + n)
        W, H = 280, 200
        im = Image.new('RGB', (W, H), (240, 196, 106))
        a = np.array(im)
        for y in range(H):
            for x in range(W):
                if (x * 3 + y * 7) % 11 == 0: a[y, x] = (255, 232, 170)
        im = Image.fromarray(a); dr = ImageDraw.Draw(im)
        for k in range(rnd.randint(10, 14)):
            s = rnd.randint(16, 40); w = int(s * (1.4 if rnd.random() < 0.3 else 1)); h = s
            x = rnd.randint(14, W - 14 - w); y = rnd.randint(14, H - 14 - h)
            c = rnd.choice(COLS)
            def torn(dx, dy):
                pts = []
                for t in range(0, w, 3): pts.append((x + t + dx, y + rnd.randint(-1, 1) + dy))
                for t in range(0, h, 3): pts.append((x + w + rnd.randint(-1, 1) + dx, y + t + dy))
                for t in range(w, 0, -3): pts.append((x + t + dx, y + h + rnd.randint(-1, 1) + dy))
                for t in range(h, 0, -3): pts.append((x + rnd.randint(-1, 1) + dx, y + t + dy))
                return pts
            dr.polygon(torn(2, 2), fill=(168, 119, 83))
            dr.polygon(torn(0, 0), fill=c)
        save(im, OUT + 'dada-arp-%d.png' % (n + 1))

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['pictures', 'numerals', 'stoppages', 'arp']): globals()[w]()
