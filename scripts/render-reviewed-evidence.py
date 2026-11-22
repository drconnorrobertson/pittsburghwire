"""Update only explicitly reviewed source blocks, authorship, dates and sitemap entries."""
from pathlib import Path
import json,re,sys
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catalog_evidence import MODEL,reviewed_links_markup
ROOT=Path(__file__).resolve().parents[1]
SITE='https://www.thepittsburghwire.com'

def render(root=ROOT):
 data=json.loads((root/'data/businesses.json').read_text());changed=[]
 for slug,row in data.items():
  if row.get('official_research',{}).get('evidence_model')!=MODEL:continue
  path=root/'directory'/slug/'index.html';html=path.read_text()
  pattern=r'<h2>Useful (?:pages from|sources for) [^<]+</h2>[\s\S]*?(?=<h2>)'
  html,n=re.subn(pattern,lambda _:reviewed_links_markup(row)+'\n',html,count=1);assert n==1,slug
  checked=date.fromisoformat(row['checked']).strftime('%B %d, %Y').replace(' 0',' ')
  html=re.sub(r'<p class="profile-byline">[\s\S]*?</p>', '<p class="profile-byline">AI-assisted profile by <a href="/about">The Pittsburgh Wire editorial</a> · Updated <time datetime="'+row['checked']+'">'+checked+'</time></p>',html,count=1)
  # This date describes the current source review, not a new publication.
  html=re.sub(r'Listing details checked [A-Za-z]+ \d+, \d{4} against','Listing details checked '+checked+' against',html,count=1)
  scripts=list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>',html,re.S));m=scripts[-1];graph=json.loads(m[1]);web=next(x for x in graph['@graph']if x.get('@type')=='WebPage')
  assert web['datePublished']==row['published'],slug
  editorial={'@type':'Organization','@id':SITE+'/#editorial','name':'The Pittsburgh Wire editorial','url':SITE+'/about/'}
  graph['@graph'][0]=editorial;web['author']={'@id':editorial['@id']};web['dateModified']=row['checked']
  html=html[:m.start(1)]+json.dumps(graph,ensure_ascii=False).replace('<','\\u003c')+html[m.end(1):]
  path.write_text(html);changed.append(slug)
 for name in ['sitemap.xml','directory-sitemap.xml']:
  path=root/name;s=path.read_text()
  for slug in changed:
   url=SITE+'/directory/'+slug+'/'
   s,n=re.subn(r'(<url>\s*<loc>'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+data[slug]['checked'],s,count=1);assert n==1,(name,slug)
  path.write_text(s)
 return changed
if __name__=='__main__':print(json.dumps({'reviewedProfiles':render()}))
