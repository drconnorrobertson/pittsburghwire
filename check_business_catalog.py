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
        research=r.get('official_research',{})
        if research.get('status')=='corroborated':
            host=urlsplit(research['url']).hostname
            links=list(research.get('links',{}).values())+research.get('topics',[])
            for link in links:
                if urlsplit(link['url']).hostname!=host:errors.append(f'{slug}: official evidence link leaves corroborated host')
                if link in research.get('topics',[]) and link['url'].replace('&','&amp;') not in page:errors.append(f'{slug}: sourced topic link missing from output')
            words=len(research.get('description_excerpt','').split())+sum(len(x['label'].split()) for x in research.get('topics',[]))
            if words>25:errors.append(f'{slug}: source excerpt budget exceeded')
        if 'source-directory classification' not in page:errors.append(f'{slug}: missing category qualification')
        if r['source'] in sources:errors.append(f'{slug}: duplicate source record')
        sources.add(r['source'])
        if url not in urls:errors.append(f'{slug}: absent from sitemap')
        if 'rel="author">Dr. Connor Robertson' not in page:errors.append(f'{slug}: missing visible byline')
        if 'name="robots" content="index, follow"' not in page:errors.append(f'{slug}: not indexable')
        if '<img' in page or 'og:image' in page:errors.append(f'{slug}: contains image')
        if len(r['source_excerpt'].split())>20:errors.append(f'{slug}: excessive source quotation')
        if urlsplit(r['website']).scheme not in ('http','https') or not urlsplit(r['website']).netloc or ' ' in r['website']:errors.append(f'{slug}: invalid website')
        graphs=re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)
        graph=json.loads(graphs[-1])['@graph']
        web=next(x for x in graph if x.get('@type')=='WebPage')
        if web['author']['@id']!=SITE+'/#founder':errors.append(f'{slug}: invalid structured author')
    original_file=ROOT/'data/original-businesses.json'
    if original_file.exists():
        for slug in json.loads(original_file.read_text()):
            markup=(ROOT/'directory'/slug/'index.html').read_text()
            if markup.count('<!-- ORIGINAL_DEPTH_START -->')!=1:errors.append(f'{slug}: missing or duplicated original profile guide')
    print(f'{len(DATA)} catalog records; {len(VERIFIED)} published profiles; {len(urls)} directory sitemap URLs; {len(errors)} errors')
    for error in errors[:30]:print('ERROR',error)
    return not errors
if __name__=='__main__':raise SystemExit(0 if check() else 1)
