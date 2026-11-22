"""Verify canonical ownership, distinct source identities and preserved facts."""
from pathlib import Path
import json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catalog_identity import duplicate_identities,identity_key
ROOT=Path(__file__).resolve().parents[1];SITE='https://www.thepittsburghwire.com';old='roaming-bean-strip-district';keep='the-roaming-bean';d=json.loads((ROOT/'data/businesses.json').read_text());assert old not in d and keep in d;assert not duplicate_identities(d)
# Same citation can document different businesses and different locations.
base={'name':'Sample Coffee','address':'1455 Smallman Street, Pittsburgh, Pennsylvania 15222','source':'https://town.example/notices'}
other=dict(base,name='Sample Bookshop',address='20480 Route 19, Suite 108, Cranberry, PA 16066');assert not duplicate_identities({'a':base,'b':other})
other=dict(base,address='42 Another Street, Pittsburgh, PA 15222');assert not duplicate_identities({'a':base,'b':other})
other=dict(base,address='1455 Smallman St., Pittsburgh, PA 15222');assert duplicate_identities({'a':base,'b':other})==[('a','b')]
for slug in ['ebisu-life-cranberry-planned','saba-origin-coffee-cranberry-planned']:assert slug in d
h=(ROOT/'directory'/keep/'index.html').read_text();assert '412-427-8822'in h and '412-337-0769'in h;assert '1455 Smallman Street'in h;assert 'AI-assisted profile by'in h
web=next(x for x in json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S)[-1])['@graph']if x.get('@type')=='WebPage');assert web['datePublished']=='2026-10-07'and web['dateModified']=='2026-11-21'
assert web['author']['@id']==SITE+'/#editorial'
rules=json.loads((ROOT/'vercel.json').read_text())['redirects']
for suffix in ['/','']:
 rule=[x for x in rules if x['source']=='/directory/'+old+suffix];assert len(rule)==1 and rule[0]['destination']=='/directory/'+keep+'/'and rule[0]['permanent']
fallback=(ROOT/'directory'/old/'index.html').read_text();assert 'noindex, follow'in fallback and SITE+'/directory/'+keep+'/'in fallback
rows=json.loads((ROOT/'data/directory-search.json').read_text());assert len(rows)==3006;assert sum(x['url']=='/directory/'+keep+'/'for x in rows)==1;assert not any(old in x['url']for x in rows)
import xml.etree.ElementTree as E
for file,count in [('sitemap.xml',3937),('directory-sitemap.xml',3006)]:
 urls=[x.text for x in E.parse(ROOT/file).findall('.//{*}loc')];assert len(urls)==count and len(set(urls))==count;assert SITE+'/directory/'+old+'/'not in urls and SITE+'/directory/'+keep+'/'in urls
for p in ROOT.rglob('*.html'):
 if '.git'not in p.parts:assert 'href="/directory/'+old+'/'not in p.read_text(),p
print(json.dumps({'canonicalProfiles':3006,'rootOwners':3937,'duplicateIdentities':0,'identityControls':3,'twoDistinctTownshipBusinessesRetained':True,'bothPhonePurposesPreserved':True,'retiredSlashRules':2,'sourcePublicationPreserved':'2026-10-07'}))
