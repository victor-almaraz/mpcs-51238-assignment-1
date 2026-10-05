# The magazines on the shelf, each set from its text (text/<issue>.md) into v25/index.html:
# a cover, then leaves (the contents with the editors' letter, the articles, the catalogue),
# each a spread whose text flows in columns (magazine.js turns them a spread at a time).
# Each issue is its own .mag, with its own ids, inks and plates; the rack above them picks one.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import html, re, os
HERE = UTIL + '/v25/'
INDEX = REPO + '/v25/index.html'

ISSUES = [  # key, title, text, element id, id prefix, the leaves' inks, plates, columns to a page
    dict(key='moire', title='Moiré', md='magazine.md', el='mag', pre='mag', inks=['m', 'c', 'm', 'y', 'o', 'c'],
         plates=['mag-contents.png', 'mag-a1.png', 'mag-a2.png', 'mag-a3.png', 'mag-a4.png', 'mag-catalogue.png'], cols=1, cover='o'),
    dict(key='event', title='Event', md='event.md', el='mag-event', pre='ev', inks=['r', 'k', 'r', 'k', 'r'],
         plates=['ev-contents.png', 'ev-a1.png', 'ev-a2.png', 'ev-a3.png', 'ev-catalogue.png'], cols=2, cover='r'),
    dict(key='gesso', title='Gesso', md='gesso.md', el='mag-gesso', pre='gs', inks=['y', 'o', 'c', 'm', 'y'],
         plates=['gs-contents.png', 'gs-a1.png', 'gs-a2.png', 'gs-a3.png', 'gs-catalogue.png'], cols=1, cover='y'),
    dict(key='cons', title='Cons', md='cons.md', el='mag-cons', pre='cn', inks=['g', 'k', 'g', 'k', 'g'],
         plates=['cn-contents.png', 'cn-a1.png', 'cn-a2.png', 'cn-a3.png', 'cn-catalogue.png'], cols=1, cover='g'),
    dict(key='silver', title='Silver', md='silver.md', el='mag-silver', pre='sv', inks=['k', 'k', 'k', 'k', 'k'],
         plates=['sv-a1.png', 'sv-contents.png', 'sv-a2.png', 'sv-a3.png', 'sv-catalogue.png'], cols=1, cover='k'),
]

def sections(text):
    out, name = {}, None
    for line in text.split('\n'):
        if line.startswith('# '): name = line[2:].strip(); out[name] = []
        elif name: out[name].append(line)
    return out

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)
    return t

def fields(lines):
    f, body = {}, []
    for ln in lines:
        m = re.match(r'^(kicker|strap|headline|subhead|names|title|standfirst|pullquote):\s*(.*)$', ln)
        if m and not body: f[m.group(1)] = m.group(2)
        else: body.append(ln)
    return f, body

def blocks(body):
    out, para = [], []
    def flush():
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
    for ln in body:
        s = ln.strip()
        if not s: flush(); continue
        m = re.match(r'^\[deck:\s*([\w-]+)\s*\|\s*(.+?)\s*\]$', s)
        if m:
            flush(); out.append('<p class="mag-deck"><button type="button" data-deck="%s">Put <i>%s</i> on the coding form</button></p>' % (m.group(1), inline(m.group(2)))); continue
        if s.startswith('## '): flush(); out.append('<h4>' + inline(s[3:]) + '</h4>'); continue
        if s.startswith('= '): flush(); out.append('<p class="mag-formula">' + inline(s[2:]) + '</p>'); continue
        para.append(s)
    flush()
    return out

def ind(lines, n): return '\n'.join(' ' * n + l for l in lines)

def leaf(ink, hid, plate, kicker, title, standfirst=None, pull=None, opener_extra=(), body=(), cls=''):
    op = [f'<figure class="mag-plate-box"><img class="mag-plate" src="assets/st/{plate}" width="264" height="96" alt=""></figure>',
          f'<p class="mag-kicker">{kicker}</p>',
          f'<h3 id="{hid}" class="mag-h" tabindex="-1">{title}</h3>']
    if standfirst: op.append(f'<p class="mag-standfirst">{inline(standfirst)}</p>')
    op += list(opener_extra)
    if pull: op.append(f'<blockquote class="mag-pull"><p>{inline(pull)}</p></blockquote>')
    return f'''    <section class="mag-leaf mag-spread{cls}" data-ink="{ink}" aria-labelledby="{hid}">
      <div class="mag-flow">
        <div class="mag-opener">
{ind(op, 10)}
        </div>
{ind(body, 8)}
      </div>
    </section>'''

def issue(cfg):
    S = sections(open(HERE + 'text/' + cfg['md']).read())
    pre, inks, plates = cfg['pre'], cfg['inks'], cfg['plates']
    cf, _ = fields(S['COVER'])
    parts = [x.strip() for x in cf['kicker'].split('·')]
    date = ' '.join('<span>%s</span>' % inline(x) for x in parts)
    tid = 'mag-title' if pre == 'mag' else pre + '-title'
    cover = f'''    <section class="mag-leaf mag-leaf-cover" data-ink="{cfg['cover']}" aria-labelledby="{tid}">
      <div class="mag-page mag-cover">
        <div class="mag-cover-top">
          <p class="mag-dateline">{date}</p>
          <h2 id="{tid}" class="mag-h" tabindex="-1"><span class="mag-big">{cfg['title']}</span> <span class="mag-sub">{inline(cf['strap'])}</span></h2>
        </div>
        <div class="mag-cover-field">
          <p class="mag-coverline"><span class="mag-cl-big">{inline(cf['headline'])}</span> <span class="mag-cl-small">{inline(cf['subhead'])}</span></p>
          <p class="mag-cover-names">{inline(cf['names'])}</p>
        </div>
      </div>
    </section>'''
    arts = sorted(k for k in S if k.startswith('ARTICLE '))
    # the leaves: 0 the cover, 1 the contents, then the articles, then the catalogue
    items = [l[2:].split('|') for l in S['CONTENTS'] if l.startswith('- ')]
    nums = [k.split()[1] for k in arts]
    def goto(n): return 2 + nums.index(n) if n in nums else 2 + len(arts)
    lis = ['<ol class="mag-contents">'] + ['  <li><span class="mag-n" aria-hidden="true">%s</span><div><button type="button" class="mag-link" data-goto="%d">%s</button><p>%s</p></div></li>'
           % (n.strip(), goto(n.strip()), inline(t.strip()), inline(d.strip())) for n, t, d in items] + ['</ol>']
    ef, ebody = fields(S['EDITORS'])
    eb = blocks(ebody)
    eb[-1] = eb[-1].replace('<p>', '<p class="mag-colophon">', 1)
    cid = 'mag-contents-h' if pre == 'mag' else pre + '-contents-h'
    leaves = [cover, leaf(inks[0], cid, plates[0], 'In this issue', 'Contents', opener_extra=lis,
                          body=['<h4 class="mag-label">' + inline(ef['title']) + '</h4>'] + eb, cls=' mag-leaf-contents')]
    for i, k in enumerate(arts):
        f, body = fields(S[k])
        b = blocks(body)
        if b and b[0].startswith('<p>'): b[0] = b[0].replace('<p>', '<p class="mag-first">', 1)
        n = k.split()[1]
        leaves.append(leaf(inks[1 + i], '%s-a%d' % (pre, int(n)), plates[1 + i], '<span class="mag-num">%s</span> %s' % (n, inline(f['kicker'])),
                           inline(f['title']), f.get('standfirst'), f.get('pullquote'), body=b))
    cf2, cbody = fields(S['CATALOGUE'])
    cat = ['<ol class="mag-cat">']
    for ln in cbody:
        if not ln.startswith('- '): continue
        did, name, desc = [x.strip() for x in ln[2:].split('|', 2)]
        cat.append(f'  <li><h4>{inline(name)}</h4><p>{inline(desc)}</p><p class="mag-deck"><button type="button" data-deck="{did}">Put <i>{inline(name)}</i> on the coding form</button></p></li>')
    cat.append('</ol>')
    catno = [x[0].strip() for x in items][-1]
    leaves.append(leaf(inks[-1], (pre + '-cat-h'), plates[-1], '<span class="mag-num">%s</span> The catalogue' % catno, inline(cf2['title']), cf2.get('standfirst'), body=cat))
    # the index under the pages: one button for each leaf
    labels = ['C', '00'] + nums + [catno]
    names = ['Cover', 'Contents'] + [fields(S[k])[0]['title'] for k in arts] + [cf2['title']]
    dots = '\n'.join('        <li><button type="button" data-goto="%d"><span class="mag-dot">%s</span><span class="mag-vh"> %s</span></button></li>' % (i, l, inline(n)) for i, (l, n) in enumerate(zip(labels, names)))
    hidden = '' if cfg['key'] == 'moire' else ' hidden'
    return f'''<div class="mag" id="{cfg['el']}" data-issue="{cfg['key']}" data-cols="{cfg['cols']}"{hidden}>
  <div class="mag-book">

{chr(10).join(leaves)}

  </div>
  <div class="mag-turn">
    <button type="button" class="mag-pill" data-turn="-1">&lsaquo; Previous page</button>
    <nav class="mag-index" aria-label="Pages of {cfg['title']}">
      <ol>
{dots}
      </ol>
    </nav>
    <p class="mag-folio" aria-live="polite"></p>
    <button type="button" class="mag-pill mag-next" data-turn="1">Next page &rsaquo;</button>
  </div>
</div>'''

def main():
    ready = [c for c in ISSUES if os.path.exists(HERE + 'text/' + c['md'])]
    rack = ['<nav class="mag-rack" aria-label="The magazines on the shelf">', '  <ul>'] + \
           ['    <li><button type="button" data-issue="%s" aria-pressed="%s">%s</button></li>' % (c['key'], 'true' if c['key'] == 'moire' else 'false', c['title']) for c in ready] + \
           ['  </ul>', '</nav>']
    body = '\n'.join(rack) + '\n' + '\n'.join(issue(c) for c in ready)
    s = open(INDEX).read()
    a = s.index('<section class="station st-mag"')
    a = s.index('>', a) + 1
    b = s.index('\n  </section>', a) + 1          # the station's own closing tag, at two spaces
    s = s[:a] + '''
<!-- The magazines on the shelf: Moiré (art and computing), Event (a Fluxus newspaper), Gesso
     (painting by rule and chance), Cons (Lisp) and Silver (black-and-white photography), the
     rack above them choosing one. After its cover, each
     issue's .mag-leaf is an article whose text flows in columns over as many spreads as it
     needs (magazine.js turns them a spread at a time); its plates are pixel pictures in
     assets/st/. -->
''' + body + '\n' + s[b:]
    open(INDEX, 'w').write(s)
    print([c['key'] for c in ready])

if __name__ == '__main__':
    main()
