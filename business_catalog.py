"""Render source-backed, text-only business profiles and searchable browse pages."""
import json, re
from html import escape
from pathlib import Path
from urllib.parse import quote
from business_depth import profile_depth, collection_depth

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'data'/'businesses.json').read_text()) if (ROOT/'data'/'businesses.json').exists() else {}
SITE='https://www.thepittsburghwire.com'
AUTHOR={'@type':'Person','@id':SITE+'/#founder','name':'Dr. Connor Robertson','url':SITE+'/founder/'}
LABELS={
    'food-and-drink':'Food & Drink','tech':'Technology','health-and-wellness':'Health & Wellness',
    'real-estate':'Real Estate','arts-and-culture':'Arts, Entertainment & Recreation','retail':'Retail',
    'professional-services':'Professional Services','trades-and-services':'Trades & Services',
    'education':'Education','finance':'Finance','automotive':'Automotive',
    'hotels-and-lodging':'Hotels & Lodging','nonprofit-and-community':'Nonprofits & Community',
}
CSS='''
.profile-layout{display:grid;grid-template-columns:minmax(0,2fr) minmax(250px,1fr);gap:32px}
.profile-copy p{margin:0 0 22px;line-height:1.8}.profile-copy h2{font-family:'Playfair Display',Georgia,serif;font-size:28px;margin:32px 0 16px}
.profile-facts{border:1px solid var(--rule);padding:24px;height:fit-content}.profile-facts dt{font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;color:var(--accent);margin-top:20px}.profile-facts dd{margin:8px 0;overflow-wrap:anywhere}.profile-facts a,.profile-copy a{text-decoration:underline;text-underline-offset:3px}
.profile-byline{margin-top:16px;font-family:'Barlow Condensed',sans-serif}.source-quote{border-left:3px solid var(--accent);padding:16px 20px;margin:20px 0;font-style:italic;background:rgba(255,255,255,.025)}
.biz-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:24px 0}.biz-card{display:block;border:1px solid var(--rule);padding:22px;text-decoration:none}.biz-card:hover{border-color:var(--accent)}.biz-name{font-family:'Playfair Display',Georgia,serif;font-size:21px;line-height:1.35}.biz-owner{font-size:14px;color:var(--smoke);margin-top:12px}.catalog-controls{display:flex;gap:16px;flex-wrap:wrap;align-items:end}.catalog-controls label{display:block}.catalog-controls input,.catalog-controls select{font:inherit;background:var(--cream);color:var(--ink);border:1px solid var(--rule);padding:12px;width:100%;margin-top:8px}.catalog-controls>div{flex:1;min-width:200px}.category-links{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}.category-links a{border:1px solid var(--rule);padding:9px 12px;font-size:14px}.biz-card[hidden]{display:none}.catalog-note{color:var(--smoke);margin:16px 0}.directory-back{display:inline-block;border:1px solid var(--accent);padding:12px 18px;margin:20px 0}
@media(max-width:850px){.profile-layout{grid-template-columns:1fr}.biz-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:550px){.biz-grid{grid-template-columns:1fr}}
'''
def schema(graph):
    return '<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')+'</script>'
def shell(page_shell,title,desc,url,body,graph):
    markup=page_shell(escape(title),escape(desc,quote=True),url,body,active_nav='/directory')
    return markup.replace('</head>','<style>'+CSS+'</style>\n'+schema(graph)+'\n</head>',1)
def write(repo,page_shell):
    base=Path(repo)/'directory'
    from directory_index import VERIFIED_CATEGORY, VERIFIED, profile_name
    names={s: (DATA[s]['name'] if s in DATA else profile_name(base/s/'index.html')) for s in VERIFIED}
    for slug,r in DATA.items():
        name=escape(r['name']);cat=r['category'];label=escape(LABELS[cat]);address=escape(r['address']);city=escape(r['city']);source=escape(r['source'],quote=True);website=escape(r['website'],quote=True)
        url=f'{SITE}/directory/{slug}/'
        peers=sorted((s for s in VERIFIED if s!=slug and VERIFIED_CATEGORY[s]==cat),key=lambda s:(DATA.get(s,{}).get('city')!=r['city'],names[s].casefold()))[:4]
        related=''.join(f'<a class="biz-card" href="/directory/{s}/"><div class="biz-name">{escape(names[s])}</div></a>' for s in peers)
        phone=(f'<dt>Phone</dt><dd><a href="tel:{escape(r["phone"],quote=True)}">{escape(r["phone"])}</a></dd>' if r['phone'] else '')
        excerpt_source=escape(r.get('source_excerpt_url',r['source']),quote=True)
        excerpt_name=escape(r.get('source_excerpt_name',r['source_name']))
        excerpt=(f'<h2>About {name}</h2><p><a href="{excerpt_source}" rel="noopener noreferrer">{excerpt_name}</a> describes the business this way:</p><blockquote class="source-quote">“{escape(r["source_excerpt"])}”</blockquote>' if r['source_excerpt'] else '')
        depth=profile_depth(r,DATA)
        body=f'''<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Business Directory</a><span>/</span><a href="/directory/{cat}/">{label}</a><span>/</span><span>{name}</span></div>
<header class="page-head"><span class="page-eyebrow">Pittsburgh area business directory · {label}</span><h1 class="page-title">{name}</h1><p class="page-deck">{escape(r['source_category'])} · {city}, Pennsylvania</p><p class="profile-byline">By <a href="/founder/" rel="author">Dr. Connor Robertson</a> · Updated <time datetime="{r['checked']}">October 7, 2026</time></p></header>
<main class="archive"><div class="profile-layout"><div class="profile-copy"><h2>{name} in the Pittsburgh area</h2><p>{name} appears in {escape(r['source_name'])} under <strong>{escape(r['source_category'])}</strong>. Its listed location is <strong>{address}</strong>. This profile brings the location, website, and available contact information together for readers exploring businesses in {city} and the Pittsburgh region.</p>
{excerpt}
{depth}
<h2>Location and contact</h2><p><a href="https://www.google.com/maps/search/?api=1&amp;query={quote(r['name']+' '+r['address'])}" rel="noopener noreferrer">Find {name} on a map</a>, or use the contact details beside this profile. The address is the location supplied by the source; an office address does not necessarily mean a walk-in storefront.</p>
<p>For current services, availability, hours, and appointments, <a href="{website}" rel="noopener noreferrer">visit {name}’s website</a>. Contact the business directly before making a trip or booking a service.</p>
<h2>Profile sources</h2><p>Listing details checked October 7, 2026 against <a href="{source}" rel="noopener noreferrer">{escape(r['source_name'])}’s business listing</a>. Inclusion documents a published business listing and does not imply a rating, affiliation, or personal visit. <a href="/contact">Send a correction</a> if details change.</p>
<a class="directory-back" href="/directory/">Explore the Pittsburgh Wire business directory →</a></div>
<aside class="profile-facts" aria-label="Business details"><h2>Business details</h2><dl><dt>Business</dt><dd>{name}</dd><dt>Listed category</dt><dd>{escape(r['source_category'])}</dd><dt>Address</dt><dd>{address}</dd>{phone}<dt>Website</dt><dd><a href="{website}" rel="noopener noreferrer">{escape(r['website'])}</a></dd><dt>Explore</dt><dd><a href="/directory/{cat}/">More {label.lower()} businesses</a></dd></dl></aside></div>
<h2 class="month-head">More {label} in the Pittsburgh Area</h2><div class="biz-grid">{related}</div></main>'''
        postal=re.search(r'\b\d{5}(?:-\d{4})?\b',r['address'])
        entity={'@type':'Organization','@id':url+'#business','name':r['name'],'url':r['website'],'address':{'@type':'PostalAddress','streetAddress':r['address'].split(', '+r['city'])[0].split(' '+r['city']+',')[0],'addressLocality':r['city'],'addressRegion':'PA','addressCountry':'US'},'sameAs':[r['source']]}
        if postal:entity['address']['postalCode']=postal.group()
        if r['phone']:entity['telephone']=r['phone']
        graph=[AUTHOR,entity,{'@type':'WebPage','@id':url+'#webpage','url':url,'name':r['name']+' | Pittsburgh Business Directory','description':r['description'],'datePublished':r['checked'],'dateModified':r['checked'],'author':{'@id':AUTHOR['@id']},'about':{'@id':entity['@id']},'isPartOf':{'@type':'WebSite','@id':SITE+'/#website','name':'The Pittsburgh Wire','url':SITE+'/','publisher':{'@type':'Organization','name':'The Pittsburgh Wire','founder':{'@id':AUTHOR['@id']}}}}, {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Business Directory','item':SITE+'/directory/'},{'@type':'ListItem','position':2,'name':LABELS[cat],'item':SITE+'/directory/'+cat+'/'},{'@type':'ListItem','position':3,'name':r['name'],'item':url}]}]
        p=base/slug/'index.html';p.parent.mkdir(exist_ok=True);p.write_text(shell(page_shell,r['name']+' | Pittsburgh Business Directory | The Pittsburgh Wire',r['description'],url,body,graph))
    browse(repo,page_shell)
    return len(DATA)
def browse(repo,page_shell):
    from directory_index import VERIFIED, VERIFIED_CATEGORY, profile_name
    base=Path(repo)/'directory'
    names={s: DATA[s]['name'] if s in DATA else profile_name(base/s/'index.html') for s in VERIFIED}
    all_slugs=sorted(VERIFIED,key=lambda s:names[s].casefold())
    for cat in [None,*LABELS]:
        slugs=[s for s in all_slugs if cat is None or VERIFIED_CATEGORY[s]==cat]
        title=f'{LABELS[cat]} Businesses in Pittsburgh' if cat else 'Pittsburgh Business Directory'
        desc=f'Browse {len(slugs):,} source-checked business profiles in Pittsburgh and nearby communities, with addresses, websites, and contact details.'
        links=''.join(f'<a href="/directory/{c}/">{escape(l)} ({sum(VERIFIED_CATEGORY[s]==c for s in VERIFIED)})</a>' for c,l in LABELS.items())
        cards=''
        for s in slugs:
            r=DATA.get(s,{})
            detail=r.get('address','Pittsburgh area')
            c=VERIFIED_CATEGORY[s]
            search=escape(' '.join([names[s],detail,LABELS[c],r.get('source_category','')]).casefold(),quote=True)
            cards+=f'<a class="biz-card" data-search="{search}" data-category="{c}" href="/directory/{s}/"><div class="biz-name">{escape(names[s])}</div><div class="biz-owner">{escape(LABELS[c])} · {escape(detail)}</div></a>\n'
        options=''.join(f'<option value="{c}">{escape(l)}</option>' for c,l in LABELS.items())
        controls=(f'<div class="catalog-controls"><div><label for="biz-search">Search business name, address, or service</label><input id="biz-search" type="search" placeholder="Find a Pittsburgh business…" autocomplete="off"></div><div><label for="biz-category">Category</label><select id="biz-category"><option value="">All categories</option>{options}</select></div></div>' if not cat else '<p><a href="/directory/">← Search all business profiles</a></p>')
        script=('''<script src="/js/business-directory.js" defer></script>''' if not cat else '')
        depth=collection_depth('services' if cat else 'locations',[s for s in slugs if s in DATA],DATA)
        body=f'''<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Business Directory</a>{('<span>/</span><span>'+escape(LABELS[cat])+'</span>') if cat else ''}</div><header class="page-head"><span class="page-eyebrow">The Pittsburgh Wire · Local business discovery</span><h1 class="page-title">{escape(title)}</h1><p class="page-deck">{escape(desc)}</p><p class="profile-byline">Published by <a href="/founder/" rel="author">Dr. Connor Robertson</a></p></header><main class="archive"><nav class="category-links" aria-label="Business categories">{links}</nav>{controls}<p class="catalog-note">Pittsburgh-area coverage includes nearby suburbs. Each profile identifies its listed location and sources. Inclusion does not constitute a rating or endorsement.</p>{depth}<p id="biz-count" aria-live="polite">{len(slugs):,} business profiles</p><div class="biz-grid">{cards}</div><noscript><p>All business profiles are listed above. Use your browser’s Find command to search by name.</p></noscript><p><a href="/contact">Submit a business or correction</a></p></main>{script}'''
        url=SITE+'/directory/'+(cat+'/' if cat else '')
        graph=[AUTHOR,{'@type':'CollectionPage','dateModified':'2026-10-07','url':url,'name':title,'description':desc,'author':{'@id':AUTHOR['@id']},'mainEntity':{'@type':'ItemList','numberOfItems':len(slugs),'itemListElement':[{'@type':'ListItem','position':i+1,'name':names[s],'url':SITE+'/directory/'+s+'/'} for i,s in enumerate(slugs)]}}]
        p=base/(cat or '')/'index.html';p.parent.mkdir(exist_ok=True);p.write_text(shell(page_shell,title+' | The Pittsburgh Wire',desc,url,body,graph))
    # A dedicated feed permits independent directory submission in Search Console.
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for s in all_slugs:
        modified=f'<lastmod>{DATA[s]["checked"]}</lastmod>' if s in DATA else ''
        xml+=f'<url><loc>{SITE}/directory/{s}/</loc>{modified}</url>\n'
    xml+='</urlset>\n'
    (Path(repo)/'directory-sitemap.xml').write_text(xml)
