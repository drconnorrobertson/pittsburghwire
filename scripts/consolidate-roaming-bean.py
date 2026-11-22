"""Consolidate one verified duplicate without regenerating unrelated profiles."""
from pathlib import Path
import json,re,sys,tempfile,shutil
from html import escape
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
OLD='roaming-bean-strip-district';KEEP='the-roaming-bean';SITE='https://www.thepittsburghwire.com'
import business_catalog,build_site,business_discovery
with tempfile.TemporaryDirectory(prefix='wire-identity-render-')as tmp:
 out=Path(tmp);shutil.copytree(ROOT,out,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','__pycache__'))
 business_catalog.write(out,build_site.page_shell);business_discovery.write(out,build_site.page_shell)
 shutil.copyfile(out/'directory'/KEEP/'index.html',ROOT/'directory'/KEEP/'index.html')
# The owner retains the earlier publication date; retired URL is a noindex fallback
# behind the permanent HTTP redirects, not a second indexable profile.
p=ROOT/'directory'/OLD/'index.html';p.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Roaming Bean listing has moved | The Pittsburgh Wire</title><meta name="robots" content="noindex, follow"><link rel="canonical" href="'+SITE+'/directory/'+KEEP+'/"></head><body><main><h1>The Roaming Bean listing has moved</h1><p>One profile now covers the café and mobile coffee business.</p><p><a href="/directory/'+KEEP+'/">View The Roaming Bean profile</a></p></main></body></html>')
changed=[]
for p in ROOT.rglob('*.html'):
 if '.git'in p.parts or p.parent.name==OLD:continue
 s=p.read_text();before=s
 # Drop the duplicated browse card, not the canonical card.
 s=re.sub(r'\s*<a\b(?=[^>]*class="biz-card")(?=[^>]*href="/directory/'+OLD+r'/?")[^>]*>[\s\S]*?</a>','',s)
 # The article's related-business list used both records for the same business.
 if str(p.relative_to(ROOT))=='news/roaming-bean-strip-district-cafe-mobile-coffee-guide/index.html':
  s=re.sub(r'<li><a href="/directory/'+OLD+r'/">[\s\S]*?</li>','',s)
 s=s.replace('/directory/'+OLD+'/', '/directory/'+KEEP+'/')
 # Only count qualifiers for this exact city/category change.
 s=s.replace('one of 219 listings in this broad category with a Pittsburgh source address.','one of 218 listings in this broad category with a Pittsburgh source address.')
 # Food category navigation counts also appear on otherwise unchanged hubs.
 s=re.sub(r'(<a\b[^>]*href="/directory/food-and-drink/"[^>]*>[^<]*?)\(384\)',r'\1(383)',s)
 rel=str(p.relative_to(ROOT))
 if rel=='directory/index.html' or rel.startswith('directory/page/'):
  s=s.replace('3,007','3,006')
 if rel=='directory/food-and-drink/index.html':
  s=s.replace('Browse 384 source-checked','Browse 383 source-checked').replace('384 business profiles','383 business profiles').replace('Pittsburgh (219)','Pittsburgh (218)')
 if rel=='locations/pittsburgh/index.html':
  s=s.replace('Explore 1054 source-checked','Explore 1053 source-checked').replace('The 1054 profiles below','The 1053 profiles below').replace('Food &amp; Drink (219)','Food &amp; Drink (218)')
 # Remove the alias from structured lists as well as their visible cards.
 def structured(m):
  graph=json.loads(m[1]);mutated=False
  def walk(obj):
   nonlocal mutated
   if isinstance(obj,dict):
    if obj.get('@type')=='CollectionPage' and 'Explore 1054 source-checked' in obj.get('description',''):
     obj['description']=obj['description'].replace('Explore 1054 source-checked','Explore 1053 source-checked');mutated=True
    if obj.get('@type')=='ItemList'and isinstance(obj.get('itemListElement'),list):
     items=obj['itemListElement'];remaining=[x for x in items if x.get('url')!=SITE+'/directory/'+OLD+'/']
     if len(remaining)!=len(items):
      mutated=True;obj['itemListElement']=remaining;obj['numberOfItems']=len(remaining)
      for i,x in enumerate(remaining):x['position']=i+1
    for v in obj.values():walk(v)
   elif isinstance(obj,list):
    for v in obj:walk(v)
  walk(graph)
  return '<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False).replace('<','\\u003c')+'</script>'if mutated else m[0]
 # Run on the pre-replacement URL so old schema ownership can be identified.
 if rel in ['directory/food-and-drink/index.html','locations/pittsburgh/index.html']:
  # Restore the alias only in its structured list prior to removal.
  originals=re.findall(r'<script type="application/ld\+json">(.*?)</script>',before,re.S)
  current=list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>',s,re.S))
  for original,match in reversed(list(zip(originals,current))):
   replacement=structured(re.match(r'<script type="application/ld\+json">(.*?)</script>','<script type="application/ld+json">'+original+'</script>',re.S))
   s=s[:match.start()]+replacement+s[match.end():]
 if s!=before:p.write_text(s);changed.append(rel)
feed=ROOT/'data/directory-search.json';rows=json.loads(feed.read_text());rows=[r for r in rows if r['url']!='/directory/'+OLD+'/'];r=business_catalog.DATA[KEEP]
for row in rows:
 if row['url']=='/directory/'+KEEP+'/':
  label=business_catalog.LABELS[r['category']];row['search']=' '.join([r['name'],r['address'],label,r['source_category']]).casefold();row['detail']=label+' · '+r['address']
assert len(rows)==3006;feed.write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
for name in ['sitemap.xml','directory-sitemap.xml']:
 p=ROOT/name;s=p.read_text();s=re.sub(r'<url>\s*<loc>'+re.escape(SITE+'/directory/'+OLD+'/')+r'</loc>[\s\S]*?</url>\s*','',s)
 s,n=re.subn(r'(<url>\s*<loc>'+re.escape(SITE+'/directory/'+KEEP+'/')+r'</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+r['checked'],s,count=1);assert n==1
 p.write_text(s)
# Correct an inherited label without implying new facts, hours or a new article.
p=ROOT/'directory/bar-marco/index.html';s=p.read_text().replace('Official restaurant and brewery information','Bar Marco restaurant website and sample menu information');p.write_text(s)
print(json.dumps({'canonical':KEEP,'retired':OLD,'updatedHTML':len(changed),'profiles':3006,'changedFiles':changed}))
