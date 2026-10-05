# The folio of influences on the bookcase, set from its text (text/folio.md) into
# v25/index.html: a sheet for each section, its entries as a catalogue's cards (the name; who
# or what, with dates; what the room takes from it), the sheets turned as the manual's pages.
import html, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.normpath(os.path.join(HERE, '../../v25/index.html'))

def inline(t):
    t = html.escape(t, quote=False)
    return re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)

def main():
    lines = open(os.path.join(HERE, 'text/folio.md')).read().split('\n')
    head, sections, cur = {}, [], None
    for ln in lines:
        m = re.match(r'^(title|intro):\s*(.*)$', ln)
        if m and not sections: head[m.group(1)] = m.group(2); continue
        if ln.startswith('# SECTION '): cur = {'name': ln[10:].strip(), 'items': []}; sections.append(cur); continue
        if ln.startswith('- ') and cur is not None:
            parts = [p.strip() for p in ln[2:].split('|')] + ['', '']
            cur['items'].append(parts[:3])
    sheets = []
    for i, sec in enumerate(sections):
        items = '\n'.join('            <li><b>%s</b> <span class="fo-who">%s</span> <span class="fo-what">%s</span></li>' % tuple(inline(p) for p in it) for it in sec['items'])
        sheets.append('''        <div class="fo-sheet"%s>
          <h3 tabindex="-1">%s</h3>
          <ul class="fo-list">
%s
          </ul>
        </div>''' % ('' if i == 0 else ' hidden', inline(sec['name']), items))
    index = '\n'.join('          <li><button type="button">%s</button></li>' % inline(s['name']) for s in sections)
    station = '''  <!-- the folio of influences from the bookcase: what the room was made from (built by util/v25/build_folio.py from text/folio.md) -->
  <section class="station st-folio-inf" id="influences" data-station="influences" aria-labelledby="influences-h" hidden>
    <div class="fo">
      <div class="fo-cover">
        <h2 id="influences-h" class="desk-tag" tabindex="-1">%s</h2>
        <p class="fo-intro">%s</p>
        <ol class="fo-index" id="fo-index" aria-label="The folio's sheets">
%s
        </ol>
      </div>
      <div class="fo-sheets">
%s
      </div>
      <div class="toolbar fo-turn">
        <button type="button" data-turn="-1">&lsaquo; Previous sheet</button>
        <p class="fo-folio" id="fo-folio" aria-live="polite"></p>
        <button type="button" data-turn="1">Next sheet &rsaquo;</button>
        <button type="button" data-go="desk">Put it back on the shelf</button>
      </div>
    </div>
  </section>
''' % (inline(head.get('title', 'Influences')), inline(head.get('intro', '')), index, '\n'.join(sheets))
    s = open(INDEX).read()
    a = s.find('  <!-- the folio of influences from the bookcase')
    if a >= 0:
        b = s.index('  </section>\n', a) + len('  </section>\n')
        s = s[:a] + station + s[b:]
    else:
        a = s.index('  <!-- the record player from the reading corner')
        s = s[:a] + station + '\n' + s[a:]
    open(INDEX, 'w').write(s)
    print(len(sections), 'sheets,', sum(len(x['items']) for x in sections), 'entries')

if __name__ == '__main__':
    main()
