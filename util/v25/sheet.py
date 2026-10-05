import sys
from art import *
import drawn, room2
from PIL import Image, ImageDraw
def all_sprites():
    S = {}
    S['print-sieve'] = room2.print_sieve(); S['print-pavilion'] = print_pavilion(); S['print-polytope'] = print_polytope()
    S['print-dada'] = room2.print_dada(); S['print-arp'] = print_arp(); S['print-taeuber'] = print_taeuber()
    S['shelf-print-paraboloids'] = room2.print_shelf(); S['shelf-print-glissandi'] = print_glissandi(); S['shelf-print-psappha'] = print_psappha()
    S['plant-fig'] = drawn.fig(); S['plant-snake'] = snake(); S['plant-palm'] = palm()
    S['plant-monstera'] = drawn.monstera(); S['plant-fern'] = fern(); S['plant-rubber'] = rubber()
    S['desk-pothos'] = drawn.pothos(); S['desk-jade'] = jade(); S['desk-cacti'] = cacti()
    S['lamp-task'] = drawn.lamp(); S['lamp-dome'] = dome(); S['lamp-angle'] = angle(); S['lamp-ceramic'] = ceramic()
    S['mug-dipped'] = room2.cut('mug.png', 3.2, 3, 4)
    S.update(mugs())
    return S
if __name__ == '__main__':
    S = all_sprites()
    sc = 3
    rows = [list(S)[i:i+3] for i in range(0, 21, 3)] + [list(S)[21:25], list(S)[25:]]
    Wd = 1400; y = 0; H = sum(max(S[n].height for n in r) * sc + 20 for r in rows)
    sheet = Image.new('RGB', (Wd, H), (60, 70, 110)); d = ImageDraw.Draw(sheet)
    for r in rows:
        x = 10
        for n in r:
            im = S[n].resize((S[n].width * sc, S[n].height * sc), Image.NEAREST)
            sheet.paste(im, (x, y + 10), im); x += im.width + 30
        y += max(S[n].height for n in r) * sc + 20
    sheet.save('sheet.png')
    for n, f in (('ogee', None), ('atomic', tile_atomic), ('trellis', tile_trellis), ('grass', tile_grass)):
        if f:
            t = f(); big = Image.new('RGB', (t.width * 6, t.height * 4))
            for i in range(6):
                for j in range(4): big.paste(t, (i * t.width, j * t.height))
            big.resize((big.width * 3, big.height * 3), Image.NEAREST).save('tile-%s.png' % n)
    print({n: S[n].size for n in S})
