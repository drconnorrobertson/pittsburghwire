"""Render reviewed business-service planning guides and their discovery links."""
import json,re
from html import escape as e
from pathlib import Path
SITE='https://www.thepittsburghwire.com'
DATE='2026-11-20'
HUB='/guides/business-service-planning/'
STYLE='''<style>.service-guide{max-width:780px;margin:0 auto}.service-guide p,.service-guide li{font-size:1.05rem;line-height:1.8}.service-guide section{margin:2rem 0}.service-guide h2{font-family:var(--font-display);font-size:1.7rem;line-height:1.25;margin:0 0 1rem}.service-guide ul{padding-left:1.4rem}.service-guide a{text-decoration:underline;overflow-wrap:anywhere}.service-guide .guide-note{border-top:1px solid var(--rule);padding-top:1rem}.service-guide .guide-date{font-size:.95rem}.service-guide-nav{padding:1.5rem 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}</style>'''
def write(repo,page_shell=None):
 root=Path(repo)
 if page_shell is None:
  from build_site import page_shell
 guides=json.loads((root/'data/service-buying-guides.json').read_text());routes=[]
 for g in guides:
  route='/guides/'+g['slug']+'/';url=SITE+route;routes.append(route)
  body='<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Business Directory</a><span>/</span><a href="'+HUB+'">Service planning</a></div>'
  body+='<header class="page-head"><span class="page-eyebrow">Pittsburgh business service planning</span><h1 class="page-title">'+e(g['title'])+'</h1><p class="page-deck">'+e(g['description'])+'</p></header><main class="archive"><article class="service-guide"><p class="guide-date">AI-assisted editorial guide · Published November 20, 2026</p><p>'+e(g['intro'])+'</p>'
  for s in g['sections']:body+='<section><h2>'+e(s['title'])+'</h2><p>'+e(s['text'])+'</p></section>'
  body+='<section><h2>Prepare this before asking for quotes</h2><ul>'+''.join('<li>'+e(x)+'</li>' for x in g['checklist'])+'</ul></section>'
  body+='<section><h2>Sources and review scope</h2><p>Public guidance checked November 20, 2026. These are editorial planning questions, not a provider ranking, an inspection, or a determination of legal or permit requirements for your project.</p><ul>'+''.join('<li><a href="'+e(x['url'],quote=True)+'">'+e(x['label'])+'</a></li>' for x in g['sources'])+'</ul></section>'
  body+='<section><h2>Continue your research</h2><ul>'+''.join('<li><a href="'+e(x['url'],quote=True)+'">'+e(x['label'])+'</a></li>' for x in g['related'])+'</ul><p><a href="'+HUB+'">Explore all service-planning guides</a>.</p></section><p class="guide-note">Directory entries provide a starting point for research. They do not establish current service availability, a credential, insurance coverage, or an endorsement. Confirm material details with the provider and the appropriate authority.</p></article></main>'
  graph=[{'@type':'Article','headline':g['title'],'description':g['description'],'datePublished':DATE,'dateModified':DATE,'mainEntityOfPage':url,'author':{'@type':'Organization','name':'The Pittsburgh Wire editorial'},'publisher':{'@type':'Organization','name':'The Pittsburgh Wire','url':SITE},'citation':[s['url'] for s in g['sources']]},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':SITE+'/'},{'@type':'ListItem','position':2,'name':'Business Directory','item':SITE+'/directory/'},{'@type':'ListItem','position':3,'name':'Service planning','item':SITE+HUB},{'@type':'ListItem','position':4,'name':g['title'],'item':url}]}]
  markup=page_shell(e(g['title']+' | The Pittsburgh Wire'),e(g['description'],quote=True),url,body,active_nav='/directory/')
  markup=markup.replace('</head>',STYLE+'<meta name="date-modified" content="'+DATE+'"><script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph}).replace('<','\\u003c')+'</script></head>')
  dest=root/route.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(markup)
 cards=''.join('<article class="story-card"><h2 class="card-headline"><a href="/guides/'+g['slug']+'/">'+e(g['title'])+'</a></h2><p>'+e(g['description'])+'</p></article>' for g in guides)
 body='<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Business Directory</a></div><header class="page-head"><span class="page-eyebrow">Before you request a quote</span><h1 class="page-title">Plan a Pittsburgh business-service project</h1><p class="page-deck">Define the assignment, compare written scopes, and identify the local or professional questions that need a direct answer.</p></header><main class="archive"><div class="service-guide"><p>These guides help a business owner move from finding a provider to preparing a useful enquiry. Each focuses on a different assignment and links to public guidance relevant to the decision. No price comparison or provider ranking is implied.</p><p>Start with the actual work, address, timetable and decision-maker. Ask candidates to identify assumptions and exclusions. A familiar name, directory entry or low starting price does not establish that two proposals cover the same work.</p></div><div class="card-grid">'+cards+'</div><div class="service-guide"><h2>Use the directory alongside the brief</h2><p><a href="/directory/">Browse Pittsburgh-area business listings</a> and follow each profile to its sources. Verify the current services and availability directly. City, county and other municipal requirements can differ; confirm the authority for the project address before relying on a permit or licensing assumption.</p><p>The guides are editorial preparation tools. They do not replace a signed scope, professional advice, a site inspection or a required approval.</p></div></main>'
 hub=page_shell('Pittsburgh Business Service Planning Guides | The Pittsburgh Wire','Planning guides for comparing Pittsburgh business service proposals, scope, costs and responsibilities.',SITE+HUB,body,active_nav='/directory/').replace('</head>',STYLE+'<meta name="date-modified" content="'+DATE+'"></head>');dest=root/HUB.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(hub)
 path=root/'directory/index.html';s=path.read_text();s=re.sub(r'<!-- service-planning:start -->.*?<!-- service-planning:end -->','',s,flags=re.S)
 block='<!-- service-planning:start --><section class="service-guide-nav"><h2 class="month-head">Prepare before choosing a provider</h2><p>Compare the assignment, responsibilities and quote details with our <a href="'+HUB+'">business-service planning guides</a>.</p></section><!-- service-planning:end -->'
 if s.count('</main>')!=1:raise ValueError('Expected one directory main element')
 path.write_text(s.replace('</main>',block+'</main>'))
 sm=root/'sitemap.xml'
 if sm.exists():
  s=sm.read_text()
  for r in routes+[HUB]:
   if '<loc>'+SITE+r+'</loc>' not in s:s=s.replace('</urlset>','<url><loc>'+SITE+r+'</loc><lastmod>'+DATE+'</lastmod></url>\n</urlset>')
  sm.write_text(s)
 return len(guides)
if __name__=='__main__':print('Service planning guides:',write(Path(__file__).resolve().parent))
