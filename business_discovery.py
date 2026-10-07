"""Connect real businesses to specific services, listed cities, and relevant reporting."""
import re
from html import escape, unescape
from pathlib import Path
from business_catalog import DATA, SITE, AUTHOR, shell
from business_depth import collection_depth, article_body_span

SERVICES={
 'accountants-and-bookkeepers':('Accountants & Bookkeepers',r'accounting|bookkeep'),
 'financial-advisors':('Financial Advisors',r'financial advisors|financial planning|investment services'),
 'insurance':('Insurance Businesses',r'insurance'),
 'law-firms':('Law Firms',r'attorney|law firm'),
 'contractors':('Contractors',r'contractor'),
 'fitness-centers':('Fitness Centers',r'fitness|health club|gymnasium'),
 'marketing-and-advertising':('Marketing & Advertising Businesses',r'marketing|advertising|public relations'),
 'consultants':('Business Consultants',r'business.*consult|management.*consult'),
 'caterers':('Caterers',r'catering'),
 'breweries-wineries-and-distilleries':('Breweries, Wineries & Distilleries',r'winer|brewer|distill'),
 'museums-and-galleries':('Museums & Galleries',r'visual arts and museums|arts, crafts & galleries|museum|art galleries'),
 'event-venues':('Event & Meeting Venues',r'event & meeting venues|entertainment venues/districts|banquet|event facilit|meeting facilit'),
 'home-improvement':('Home Improvement Businesses',r'home/home improvement|home improvement|landscape and lawn|landscaping|roofing|plumbing'),
 'automotive-dealers':('Automotive Dealers',r'automobile - dealers|automotive dealership|auto.*dealers'),
}
def slugify(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def collections():
    groups=[]
    for slug,(label,pattern) in SERVICES.items():
        slugs=[s for s,r in DATA.items() if re.search(pattern,r['source_category'],re.I)]
        if len(slugs)>=8:groups.append(('services',slug,label+' in the Pittsburgh Area',slugs))
    cities=sorted(set(r['city'] for r in DATA.values()))
    for city in cities:
        slugs=[s for s,r in DATA.items() if r['city']==city]
        if len(slugs)>=8:groups.append(('locations',slugify(city),city+' Business Directory',slugs))
    return groups
def write(repo,page_shell):
    root=Path(repo);groups=collections()
    for section,slug,title,slugs in groups:
        slugs.sort(key=lambda s:DATA[s]['name'].casefold())
        url=f'{SITE}/{section}/{slug}/'
        desc=f'Explore {len(slugs)} source-checked business profiles. Compare listed categories, addresses, websites, and contact details in The Pittsburgh Wire directory.'
        cards=''.join(f'<a class="biz-card" href="/directory/{s}/"><div class="biz-name">{escape(DATA[s]["name"])}</div><div class="biz-owner">{escape(DATA[s]["source_category"])}<br>{escape(DATA[s]["address"])}</div></a>' for s in slugs)
        text=('These businesses share the listed service categories shown below. Categories come from their source listings; compare each provider’s services and contact the business directly about the work you need.' if section=='services' else 'These profiles use the city or community shown in the source address. A Pittsburgh mailing address can also cover nearby suburbs; check the map and full address for the actual location.')
        depth=collection_depth(section,slugs,DATA)
        body=f'<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Business Directory</a><span>/</span><span>{escape(title)}</span></div><header class="page-head"><span class="page-eyebrow">Find a local business</span><h1 class="page-title">{escape(title)}</h1><p class="page-deck">{escape(desc)}</p><p class="profile-byline">By <a href="/founder/" rel="author">Dr. Connor Robertson</a></p></header><main class="archive"><p>{text}</p>{depth}<p class="catalog-note">Listings are alphabetical. Each profile links to its sources and business website.</p><div class="biz-grid">{cards}</div><a class="directory-back" href="/directory/">Search the complete Pittsburgh business directory →</a></main>'
        graph=[AUTHOR,{'@type':'CollectionPage','dateModified':'2026-10-07','name':title,'url':url,'author':{'@id':AUTHOR['@id']},'mainEntity':{'@type':'ItemList','numberOfItems':len(slugs),'itemListElement':[{'@type':'ListItem','position':i+1,'name':DATA[s]['name'],'url':SITE+'/directory/'+s+'/'} for i,s in enumerate(slugs)]}}]
        p=root/section/slug/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(shell(page_shell,title+' | The Pittsburgh Wire',desc,url,body,graph))
    # Visible navigation exposes the collections without requiring JavaScript.
    hub=root/'directory'/'index.html';markup=hub.read_text()
    links=''.join(f'<a href="/{section}/{slug}/">{escape(title)} ({len(slugs)})</a>' for section,slug,title,slugs in groups)
    block=f'<h2 class="month-head">Browse by Service or Community</h2><nav class="category-links" aria-label="Services and communities">{links}</nav>'
    markup=markup.replace('<div class="catalog-controls">',block+'<div class="catalog-controls">',1);hub.write_text(markup)
    for s,r in DATA.items():
        relevant=[g for g in groups if s in g[3]]
        if relevant:
            p=root/'directory'/s/'index.html';markup=p.read_text()
            links=' · '.join(f'<a href="/{sec}/{slug}/">{escape(title)}</a>' for sec,slug,title,_ in relevant)
            markup=markup.replace('<dt>Explore</dt>',f'<dt>More local options</dt><dd>{links}</dd><dt>Explore</dt>',1);p.write_text(markup)
    return len(groups)
def link_news(repo,articles):
    root=Path(repo);matched={};count=0
    def normalize(s):return re.sub(r'[^a-z0-9]+',' ',unescape(s).lower()).strip()
    for a in articles:
        p=root/'news'/a['slug']/'index.html';markup=p.read_text();original=markup
        markup=re.sub(r'\s*<!-- BUSINESS_LINKS_START -->.*?<!-- BUSINESS_LINKS_END -->','\n',markup,flags=re.S)
        span=article_body_span(markup)
        if not span:continue
        plain=' '+normalize(re.sub('<[^>]+>',' ',markup[span[0]:span[1]]))+' '
        slugs=[s for s,r in DATA.items() if len(normalize(r['name']))>=9 and len(normalize(r['name']).split())>=2 and ' '+normalize(r['name'])+' ' in plain]
        if slugs:
            links=''.join(f'<li><a href="/directory/{s}/">{escape(DATA[s]["name"])}</a> — listed as {escape(DATA[s]["source_category"])} at {escape(DATA[s]["address"])}. <a href="{escape(DATA[s]["source"],quote=True)}" rel="noopener noreferrer">Directory source</a>.</li>' for s in slugs[:5])
            block=f'<!-- BUSINESS_LINKS_START --><section><h2>Businesses in This Story</h2><p>For current contact research, these related directory records provide source-linked locations and official websites. This directory context was checked October 7, 2026; it does not change the reporting date or establish that a past project or announcement has since been completed.</p><ul>{links}</ul></section><!-- BUSINESS_LINKS_END -->'
            markup=markup[:span[1]].rstrip()+'\n'+block+'\n'+markup[span[1]:];count+=1
            markup=re.sub(r'("dateModified"\s*:\s*")[^"]+(")',lambda m:m[1]+'2026-10-07'+m[2],markup)
            for s in slugs[:5]:matched.setdefault(s,[]).append(a)
        span=article_body_span(markup)
        if span:
            words=len(re.sub('<[^>]+>',' ',markup[span[0]:span[1]]).split())
            reading=max(1,(words+219)//220)
            markup=re.sub(r'(<span class="article-reading-time">)[^<]*(</span>)',lambda m:m[1]+str(reading)+' min read'+m[2],markup)
        if markup!=original:p.write_text(re.sub(r'[ \t]+\n','\n',markup))
    for s,news in matched.items():
        p=root/'directory'/s/'index.html';markup=p.read_text()
        links=''.join(f'<li><a href="/news/{a["slug"]}/">{escape(a["title"])}</a></li>' for a in news[:3])
        markup=markup.replace('</main>',f'<h2 class="month-head">Related Pittsburgh Wire Coverage</h2><ul>{links}</ul></main>',1);p.write_text(markup)
    return count
