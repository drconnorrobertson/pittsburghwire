"""Validate business facts, profile authorship, and complete directory discovery."""
import json, re
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from business_catalog import DATA, SITE, LABELS
from directory_index import VERIFIED

ROOT=Path(__file__).resolve().parent
def check():
    errors=[]
    urls={x.text for x in ET.parse(ROOT/'directory-sitemap.xml').findall('.//{*}loc')}
    if len(urls)!=len(VERIFIED):errors.append('Directory sitemap count differs from published profiles')
    names=set();sources=set()
    for slug,r in DATA.items():
        page=(ROOT/'directory'/slug/'index.html').read_text()
        url=SITE+'/directory/'+slug+'/'
        for key in ('name','address','city','website','source','source_category','category','checked'):
            if not r.get(key):errors.append(f'{slug}: empty {key}')
        if r['category'] not in LABELS:errors.append(f'{slug}: invalid category')
        name=re.sub('[^a-z0-9]','',r['name'].lower())
        if name in names:errors.append(f'{slug}: duplicate business name')
        names.add(name)
        if r['source'] in sources:errors.append(f'{slug}: duplicate source record')
        sources.add(r['source'])
        if url not in urls:errors.append(f'{slug}: absent from sitemap')
        if 'rel="author">Dr. Connor Robertson' not in page:errors.append(f'{slug}: missing visible byline')
        if 'name="robots" content="index, follow"' not in page:errors.append(f'{slug}: not indexable')
        if '<img' in page or 'og:image' in page:errors.append(f'{slug}: contains image')
        if len(r['source_excerpt'].split())>20:errors.append(f'{slug}: excessive source quotation')
        if urlsplit(r['website']).scheme not in ('http','https'):errors.append(f'{slug}: invalid website')
        graphs=re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)
        graph=json.loads(graphs[-1])['@graph']
        web=next(x for x in graph if x.get('@type')=='WebPage')
        if web['author']['@id']!=SITE+'/#founder':errors.append(f'{slug}: invalid structured author')
    print(f'{len(DATA)} catalog records; {len(VERIFIED)} published profiles; {len(urls)} directory sitemap URLs; {len(errors)} errors')
    for error in errors[:30]:print('ERROR',error)
    return not errors
if __name__=='__main__':raise SystemExit(0 if check() else 1)
