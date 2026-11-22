"""Verify the researched profile without treating older catalog errors as fixed."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];URL='https://www.thepittsburghwire.com/directory/gi-jin/'
class P(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.h1=0;self.canonical=[];self.schemas=[];self.script=None;self.parts=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if t=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
  if t=='link'and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if t=='a'and a.get('href'):self.links.append(a['href'])
  if t=='script'and a.get('type')=='application/ld+json':self.script=[]
 def handle_data(self,d):
  self.parts.append(d)
  if self.script is not None:self.script.append(d)
 def handle_endtag(self,t):
  if t=='script'and self.script is not None:self.schemas.append(json.loads(''.join(self.script)));self.script=None
page=P();page.feed((ROOT/'directory/gi-jin/index.html').read_text());assert page.h1==1 and page.canonical==[URL] and 'noindex'not in page.meta['robots']
for link in['https://gi-jin.com/','https://gi-jin.com/menu/','https://gi-jin.com/contact-us/','https://www.visitpittsburgh.com/directory/gi-jin/','tel:+1-412-332-6939','/directory/food-and-drink/','/neighborhoods/downtown/']:assert link in page.links,link
assert 'http://www.richarddeshantz.com'not in page.links
nodes=[n for obj in page.schemas for n in obj.get('@graph',[obj])];web=next(n for n in nodes if n.get('@type')=='WebPage');biz=next(n for n in nodes if n.get('@id')==URL+'#business')
assert web['datePublished']=='2026-10-07'and web['dateModified']=='2026-11-21'and web['author']['@id']=='https://www.thepittsburghwire.com/#editorial'
assert biz['url']=='https://gi-jin.com/'and biz['telephone']=='+1-412-332-6939'
text=' '.join(page.parts)
for term in['3% operational fee','separate from gratuity','Tuesday through Saturday, 5–10 p.m.','AI-assisted profile by The Pittsburgh Wire editorial','no booking' ]:
 assert term.casefold()in text.casefold(),term
for path in['data/businesses.json','data/profile-features.json']:
 before=json.loads(subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT));after=json.loads((ROOT/path).read_text());before.pop('gi-jin',None);after.pop('gi-jin',None);assert before==after,path
for path in['sitemap.xml','directory-sitemap.xml']:
 def rows(s):return {e.find('{*}loc').text:ET.tostring(e)for e in ET.fromstring(s)if e.find('{*}loc')is not None}
 before=rows(subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT));after=rows((ROOT/path).read_bytes());assert set(before)==set(after)
 for url in before:
  if url!=URL:assert before[url]==after[url],url
 assert b'2026-11-21'in after[URL]
print(json.dumps({'profile':'gi-jin','officialNavigation':'passed','publicationDate':'2026-10-07','revisionDate':'2026-11-21','editorialAttribution':'passed','phoneAndWebsiteSchema':'passed','otherCatalogRowsAndFeatures':'unchanged','sitemapOwnerSetsAndOtherDates':'unchanged'}))
