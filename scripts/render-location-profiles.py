"""Select reviewed location profiles and reconcile their existing browse cards."""
from pathlib import Path
from html import escape
import tempfile,shutil,sys,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import business_catalog,build_site,business_discovery,industry_profile_context
from catalog_locations import display_location
SLUGS=('apex-junk-removal-hauling','concept-art-gallery','debatin-piano-service')
with tempfile.TemporaryDirectory(prefix='wire-location-render-')as name:
 out=Path(name);shutil.copytree(ROOT,out,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','__pycache__'))
 business_catalog.write(out,build_site.page_shell)
 business_discovery.write(out,build_site.page_shell)
 context=industry_profile_context.CONTEXT
 try:
  industry_profile_context.CONTEXT={s:context[s]for s in SLUGS}
  industry_profile_context.write(out)
 finally:industry_profile_context.CONTEXT=context
 for slug in SLUGS:
  path=out/'directory'/slug/'index.html';html=path.read_text();guide=context[slug][3];article=(out/'news'/guide/'index.html').read_text()
  heading=re.search(r'<h1[^>]*>([\s\S]*?)</h1>',article).group(1);heading=re.sub('<[^>]+>','',heading)
  coverage='<h2 class="month-head">Related Pittsburgh Wire Coverage</h2><ul><li><a href="/news/'+guide+'">'+heading+'</a></li></ul>'
  html=html.replace('<!-- INDUSTRY_CONTEXT_START -->',coverage+'<!-- INDUSTRY_CONTEXT_START -->',1);path.write_text(html)
 for slug in SLUGS:
  path=Path('directory')/slug/'index.html';shutil.copyfile(out/path,ROOT/path)
# Existing paginated cards keep their structure; only the three researched
# location displays/search strings change. No cards or pages are added.
changed=[]
for path in ROOT.rglob('*.html'):
 if '.git'in path.parts:continue
 text=path.read_text();old=text
 for slug in SLUGS:
  row=business_catalog.DATA[slug];location=display_location(row);label=business_catalog.LABELS[row['category']]
  pattern=r'<a\b[^>]*href="/directory/'+re.escape(slug)+r'/?"[^>]*>[\s\S]*?</a>'
  def card(m):
   tag=m.group(0)
   if 'class="biz-owner"'not in tag:return tag
   detail=escape(row['source_category'])+'<br>'+escape(location)if'<br'in tag else escape(label+' · '+location)
   tag=re.sub(r'(<div class="biz-owner">)[\s\S]*?(</div>)',lambda x:x.group(1)+detail+x.group(2),tag,count=1)
   search=escape(' '.join([row['name'],location,label,row['source_category']]).casefold(),quote=True)
   return re.sub(r'data-search="[^"]*"',lambda x:'data-search="'+search+'"',tag)
  text=re.sub(pattern,card,text)
 if path.parent.name in business_catalog.DATA:
  r=business_catalog.DATA[path.parent.name]
  if r['category']=='trades-and-services'and r['city']=='Pittsburgh':
   text=text.replace('with a Pittsburgh source address.','with a published Pittsburgh location or related service coverage.')
 if str(path.relative_to(ROOT)).startswith('locations/')and any('/directory/'+s+'/'in text for s in ['apex-junk-removal-hauling','debatin-piano-service']):
  text=text.replace('These profiles use the city or community shown in the source address. A Pittsburgh mailing address can also cover nearby suburbs; check the map and full address for the actual location.','These profiles group published locations and related service coverage by community. Service coverage does not identify a public storefront. Open each profile for its address or service-area information and source.')
 if text!=old:path.write_text(text);changed.append(str(path.relative_to(ROOT)))
feed=ROOT/'data/directory-search.json';rows=json.loads(feed.read_text())
for entry in rows:
 slug=entry['url'].strip('/').split('/')[-1]
 if slug not in SLUGS:continue
 row=business_catalog.DATA[slug];label=business_catalog.LABELS[row['category']];location=display_location(row)
 entry['search']=' '.join([row['name'],location,label,row['source_category']]).casefold();entry['detail']=label+' · '+location
feed.write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
for path in['sitemap.xml','directory-sitemap.xml']:
 p=ROOT/path;text=p.read_text()
 for slug in SLUGS:
  url=business_catalog.SITE+'/directory/'+slug+'/'
  pattern=r'(<url>\s*<loc>'+re.escape(url)+r'</loc>[\s\S]*?<lastmod>)[^<]+(</lastmod>)'
  text,count=re.subn(pattern,lambda m:m.group(1)+business_catalog.DATA[slug]['checked']+m.group(2),text,count=1);assert count==1,(path,slug)
 p.write_text(text)
print(json.dumps({'renderedProfiles':3,'browsePagesUpdated':len(changed),'profileSlugs':SLUGS,'searchRowsUpdated':3,'cardPages':changed}))
