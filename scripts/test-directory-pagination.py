#!/usr/bin/env python3
"""Regression: one-pass pagination keeps every listing once, then stays stable."""
import hashlib
import html
import json
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('class') == 'biz-card':
            self.urls.append(attrs['href'])

rows = json.loads((ROOT / 'data/directory-search.json').read_text())[:121]
assert len(rows) == 121
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    for directory in ['scripts', 'directory', 'data']:
        (base / directory).mkdir()
    shutil.copy(ROOT / 'scripts/paginate-directory.cjs', base / 'scripts')
    cards = ''.join(
        '<a class="biz-card" data-search="{}" data-category="{}" href="{}">'
        '<div class="biz-name">{}</div><div class="biz-owner">{}</div></a>'.format(
            *(html.escape(r[k], quote=True) for k in ['search', 'category', 'url', 'name', 'detail']))
        for r in rows)
    # The summary is intentionally replaced by longer text before cards are sliced.
    markup = ('<html><head><title>Directory</title><link rel="canonical" '
              'href="https://www.thepittsburghwire.com/directory/"></head><body>'
              '<p>The 121 profiles below span these broad categories: retail.</p>'
              '<p id="biz-count">121 profiles</p><div class="biz-grid">' + cards +
              '</div><noscript>All profiles</noscript></body></html>')
    (base / 'directory/index.html').write_text(markup)
    (base / 'sitemap.xml').write_text('<urlset><url><loc>https://www.thepittsburghwire.com/directory/</loc></url></urlset>')
    hashes = None
    for run in range(2):
        subprocess.run(['node', str(base / 'scripts/paginate-directory.cjs')], check=True, capture_output=True)
        pages = [base / 'directory/index.html', base / 'directory/page/2/index.html', base / 'directory/page/3/index.html']
        seen = []
        for page, expected in zip(pages, [60, 60, 1]):
            text = page.read_text()
            parser = Cards()
            parser.feed(text)
            assert len(parser.urls) == expected, (run, page, len(parser.urls))
            assert '<div class="bi<a' not in text
            seen.extend(parser.urls)
        assert seen == [r['url'] for r in rows]
        assert len(set(seen)) == 121
        current = [hashlib.sha256(p.read_bytes()).hexdigest() for p in pages]
        if hashes is not None:
            assert current == hashes, 'Repeated pagination changed HTML'
        hashes = current
print('PASS: all 121 source listings appear once across 60/60/1 cards; two passes produce identical HTML')
