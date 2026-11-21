"""Check browse link preservation, search order and repeatable category cleanup."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

script = Path(__file__).with_name('format-directory.py')
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for directory in ('scripts', 'data', 'directory', 'services', 'locations'):
        (root / directory).mkdir()
    shutil.copy(script, root / 'scripts')
    records = {'example': {'source_category': 'Accounting, Payroll, Accounting, Payroll'}}
    (root / 'data/businesses.json').write_text(json.dumps(records))
    page = root / 'directory/index.html'
    page.write_text('<html><head><title>Directory</title></head><body>'
        '<h2 class="month-head">Browse by Service or Community</h2>'
        '<nav class="category-links" aria-label="Services and communities">'
        '<a href="/services/accountants/">Accountants</a>'
        '<a href="/locations/pittsburgh/">Pittsburgh</a></nav>'
        '<div class="catalog-controls"><div><label for="biz-search">Search</label>'
        '<input id="biz-search"></div><div><select><option>All</option></select></div></div>'
        '<p>Accounting, Payroll, Accounting, Payroll</p>'
        '<time datetime="2026-10-07">October 7, 2026</time></body></html>')
    hashes = []
    for run in range(2):
        subprocess.run(['python3', str(root / 'scripts/format-directory.py')], check=True, capture_output=True)
        text = page.read_text()
        hashes.append(hashlib.sha256(page.read_bytes()).hexdigest())
        assert text.count('href="/services/accountants/"') == 1
        assert text.count('href="/locations/pittsburgh/"') == 1
        assert text.count('<details ') == 2
        assert text.index('id="biz-search"') < text.index('<details ')
        assert '<p>Accounting, Payroll</p>' in text
        assert 'datetime="2026-10-07"' in text
    assert hashes[0] == hashes[1], 'A repeated formatting pass changed the output'
print('PASS: search precedes grouped browse links; every link and original date survives; formatting is repeatable')
