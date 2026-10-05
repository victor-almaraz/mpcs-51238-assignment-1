# the ground under each paper's tile, after a lighting build, into decor.js and style.css
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import json, re
V = REPO + '/v25/'
def main():
    g = json.load(open(UTIL + '/v25/grounds.json'))
    s = open(V + 'decor.js').read()
    a = s.index('  var GROUND = {'); b = s.index('};', a) + 2
    s = s[:a] + '  var GROUND = { ' + ',\n    '.join('%s: { %s }' % (t, ', '.join("%s: '%s'" % (p, c) for p, c in g[t].items())) for t in ('evening', 'morning', 'night')) + ' };' + s[b:]
    open(V + 'decor.js', 'w').write(s)
    c = open(V + 'style.css').read()
    for p in ('ogee', 'atomic', 'trellis', 'grass'):
        pat = r"(\.desk\[data-paper=\"%s\"\] \{[^}]*--paper-blue: )#[0-9a-f]{6}" % p if p != 'ogee' else r"(--floor-tile: url\(assets/evening/floor-tile.png\); --paper-blue: )#[0-9a-f]{6}"
        c, k = re.subn(pat, r"\g<1>" + g['evening'][p], c); assert k == 1, p
    open(V + 'style.css', 'w').write(c)
    print('synced')

if __name__ == '__main__':
    main()
