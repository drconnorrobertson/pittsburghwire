#!/usr/bin/env python3
"""Keep source-backed directory pages readable without changing listing facts."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'data/businesses.json').read_text())
replacements = {}
for record in records.values():
    original = record.get('source_category', '')
    parts = [part.strip() for part in original.split(',')]
    seen = set()
    unique = []
    for part in parts:
        if part.casefold() not in seen:
            seen.add(part.casefold())
            unique.append(part)
    if len(unique) < len(parts):
        replacements[html.escape(original)] = html.escape(', '.join(unique))

changed = []
normalized = 0
grouped = 0
for section in ('directory', 'services', 'locations'):
    for path in (ROOT / section).rglob('index.html'):
        original = text = path.read_text()
        # One category sequence can contain a shorter duplicate sequence.
        # Reach a stable result in this pass so repeated builds are identical.
        for attempt in range(10):
            before_categories = text
            for old, new in replacements.items():
                if old in text:
                    normalized += text.count(old)
                    text = text.replace(old, new)
            if text == before_categories:
                break
        else:
            raise AssertionError('Category normalization did not converge')

        pattern = r'<h2 class="month-head">Browse by Service or Community</h2><nav class="category-links" aria-label="Services and communities">(.*?)</nav>'
        match = re.search(pattern, text, re.S)
        if match:
            links = re.findall(r'<a\b[^>]*href="(/[^"]*)"[^>]*>.*?</a>', match[1], re.S)
            anchors = re.findall(r'<a\b[^>]*>.*?</a>', match[1], re.S)
            groups = [('service', 'services', 'Browse by service'), ('community', 'locations', 'Browse by community')]
            items = []
            for label, prefix, heading in groups:
                selected = [a for href, a in zip(links, anchors) if href.startswith('/'+prefix+'/')]
                if selected:
                    items.append('<details class="directory-browse"><summary>'+heading+' <span>('+str(len(selected))+')</span></summary><nav class="category-links" aria-label="Browse by '+label+'">'+''.join(selected)+'</nav></details>')
            assert items, 'Expected service and community links'
            text = text[:match.start()] + text[match.end():]
            control = re.search(r'<div class="catalog-controls">.*?</select></div></div>', text, re.S)
            assert control, 'Cannot place directory browse links after search'
            block = '<!-- directory-browse-format:start --><div class="directory-browse-groups">'+''.join(items)+'</div><!-- directory-browse-format:end -->'
            text = text[:control.end()] + block + text[control.end():]
            grouped += 1
        if text != original:
            path.write_text(text)
            changed.append(str(path.relative_to(ROOT)))

print(json.dumps({'formattedPages':len(changed),'groupedBrowsePages':grouped,'repeatedCategoryDisplaysCleaned':normalized}))
