"""Test published-location semantics, source evidence and selective rendering."""
from pathlib import Path
from html.parser import HTMLParser
from copy import deepcopy
import sys,json,re,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog_locations import location_errors,display_location
DATA=json.loads((ROOT/'data/businesses.json').read_text());SLUGS=['apex-junk-removal-hauling','concept-art-gallery','debatin-piano-service']
class Page(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.canonical=[];self.h1=0;self.links=[];self.script=None;self.schemas=[];self.text=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if t=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
  if t=='link'and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if t=='a'and a.get('href'):self.links.append(a['href'])
  if t=='script'and a.get('type')=='application/ld+json':self.script=[]
 def handle_data(self,d):
  self.text.append(d)
  if self.script is not None:self.script.append(d)
 def handle_endtag(self,t):
  if t=='script'and self.script is not None:self.schemas.append(json.loads(''.join(self.script)));self.script=None
for slug in SLUGS:
 r=DATA[slug];assert not location_errors(r);url='https://www.thepittsburghwire.com/directory/'+slug+'/'
 p=Page();p.feed((ROOT/'directory'/slug/'index.html').read_text());assert p.h1==1 and p.canonical==[url]and'noindex'not in p.meta['robots'];nodes=[n for o in p.schemas for n in o.get('@graph',[o])];biz=next(n for n in nodes if n.get('@id')==url+'#business');web=next(n for n in nodes if n.get('@type')=='WebPage');assert web['datePublished']=='2026-10-13'and web['dateModified']=='2026-11-21';assert web['author']['@id']=='https://www.thepittsburghwire.com/#editorial'
 assert '/locations/pittsburgh/'in p.links and any('/news/pittsburgh-'in link for link in p.links)
 assert (ROOT/'directory'/slug/'index.html').read_text().count('<!-- INDUSTRY_CONTEXT_START -->')==1
 if r.get('address_kind')=='service_area':
  assert 'address'not in biz and 'geo'not in biz and biz['areaServed']==r['area_served'];assert not any('google.com/maps/search/'in a for a in p.links);assert r['area_served_source']in p.links;assert 'Service area'in ' '.join(p.text);assert '<strong></strong>'not in (ROOT/'directory'/slug/'index.html').read_text()
 else:assert biz['address']['streetAddress']=='1031 South Braddock Avenue'and biz['address']['postalCode']=='15218'
# Declaring a mode alone is not enough to bypass the required evidence.
base=deepcopy(DATA['apex-junk-removal-hauling'])
for field,value in [('area_served',''),('area_served_source','https://unrelated.example/'),('address','Invented street')]:
 bad=deepcopy(base);bad[field]=value;assert location_errors(bad),(field,value)
bad=deepcopy(base);bad.pop('address_kind');assert location_errors(bad)
bad=deepcopy(DATA['concept-art-gallery']);bad['address']='';assert location_errors(bad)
old=json.loads(subprocess.check_output(['git','show','HEAD:data/businesses.json'],cwd=ROOT));new=deepcopy(DATA)
for slug in SLUGS:old.pop(slug);new.pop(slug)
assert old==new,'Unrelated source records changed'
oldfeed=json.loads(subprocess.check_output(['git','show','HEAD:data/directory-search.json'],cwd=ROOT));newfeed=json.loads((ROOT/'data/directory-search.json').read_text());assert len(oldfeed)==len(newfeed)==3007
for before,after in zip(oldfeed,newfeed):
 slug=after['url'].strip('/').split('/')[-1]
 if slug in SLUGS:assert display_location(DATA[slug])in after['detail']
 else:assert before==after
for path in['sitemap.xml','directory-sitemap.xml']:
 def rows(text):return {e.find('{*}loc').text:ET.tostring(e)for e in ET.fromstring(text)if e.find('{*}loc')is not None}
 a=rows(subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT));b=rows((ROOT/path).read_bytes());assert set(a)==set(b)
 changed={'https://www.thepittsburghwire.com/directory/'+s+'/'for s in SLUGS}
 for u in a:
  if u not in changed:assert a[u]==b[u],u
# Report remaining catalog failures separately; they must not mask a new
# location regression or prevent later fixes to unrelated records.
r=subprocess.run([sys.executable,'check_business_catalog.py'],cwd=ROOT,capture_output=True,text=True);errors=[x for x in r.stdout.splitlines()if x.startswith('ERROR ')];assert r.returncode in (0,1) and 'catalog records;'in r.stdout and not any(any(s in x for s in SLUGS)for x in errors)
print(json.dumps({'profiles':3,'verifiedStreetAddresses':1,'sourcedServiceAreas':2,'noInventedStreetOrMap':'passed','sourceEvidenceNegativeControls':5,'originalPublication':'2026-10-13','revision':'2026-11-21','searchRowsUpdated':3,'sitemapOwnersAndOtherDates':'preserved','otherSourceRecords':'unchanged','remainingCatalogErrors':len(errors)}))
