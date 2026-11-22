"""Check reviewed destinations, street correction and unchanged publication history."""
from pathlib import Path
from copy import deepcopy
from urllib.parse import unquote
import json,re,sys,xml.etree.ElementTree as E
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catalog_evidence import evidence_errors,reviewed_links_markup
R=Path(__file__).resolve().parents[1];d=json.loads((R/'data/businesses.json').read_text());slugs=['circa-barbershop-pittsburgh','lao-sze-chuan-sheraton-drive','7-brew-natrona-heights']
for slug in slugs:
 r=d[slug];h=(R/'directory'/slug/'index.html').read_text();assert reviewed_links_markup(r)in h;assert r['editorial_author']
 g=json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S)[-1])['@graph'];w=next(x for x in g if x.get('@type')=='WebPage');assert w['datePublished']==r['published']=='2026-10-13';assert w['dateModified']=='2026-11-21';assert w['author']['@id'].endswith('/#editorial')
 for link in r['official_research']['links'].values():assert not evidence_errors(r['official_research'],link),(slug,link)
# Official chain provenance must bind the exact destination and a source on the location host.
r=d['7-brew-natrona-heights']['official_research'];link=r['links']['services'];assert link['evidence']['relationship']=='official_chain'
for key,value in [('source','https://unrelated.example/'),('target','https://7brew.com/unreviewed'),('relationship','trusted_chain'),('checked',''),('note','')]:
 bad=deepcopy(link);bad['evidence'][key]=value;assert evidence_errors(r,bad),key
bad=deepcopy(r);bad.pop('evidence_model');assert evidence_errors(bad,link)
row=d['7-brew-natrona-heights'];assert row['address']=='1425 Freeport Road, Natrona Heights, PA 15065'
for f in ['directory/7-brew-natrona-heights/index.html','news/7-brew-natrona-heights-freeport-road-opening-guide/index.html']:
 h=(R/f).read_text();assert '1425 Freeport' in h and '1421' not in h and '/1425-freeport-road'in h,f
h=(R/'directory/7-brew-natrona-heights/index.html').read_text();assert '1425 Freeport'in unquote(h),'Map street number differs'
rows=json.loads((R/'data/directory-search.json').read_text());search=next(x for x in rows if x['url']=='/directory/7-brew-natrona-heights/');assert '1425 Freeport'in search['detail'] and '1421' not in json.dumps(search)
for f in ['sitemap.xml','directory-sitemap.xml']:
 entries=list(E.parse(R/f).getroot());urls=[x.find('{*}loc').text for x in entries];assert len(urls)==len(set(urls))==(3937 if f=='sitemap.xml'else 3006)
 for slug in slugs:
  e=next(x for x in entries if x.find('{*}loc').text=='https://www.thepittsburghwire.com/directory/'+slug+'/');assert e.find('{*}lastmod').text=='2026-11-21'
print(json.dumps({'reviewedProfiles':3,'resolvedExternalLinks':4,'officialChainNegativeControls':6,'address':'1425 Freeport Road','publicationDates':'2026-10-13 preserved','rootOwners':3937,'directoryOwners':3006}))
