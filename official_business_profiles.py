"""Render individually sourced editorial directory entries without altering legacy profiles."""
from html import escape as e
from pathlib import Path
import json,re
from datetime import date

SITE='https://www.thepittsburghwire.com'
STYLE='''<style>.official-profile{max-width:780px;margin:auto}.official-profile p,.official-profile li{line-height:1.8}.official-profile h2{margin-top:2rem;font-family:var(--font-display);font-size:1.7rem}.official-profile a{overflow-wrap:anywhere;text-decoration:underline}.official-profile .contact-link{display:inline-flex;align-items:center;min-height:44px;padding:6px 0}.official-profile dl{border:1px solid var(--rule);padding:20px}.official-profile dt{font-weight:bold;margin-top:14px}.official-profile dd{margin:4px 0;overflow-wrap:anywhere}.page-title{overflow-wrap:anywhere}</style>'''
def write(root,row,slug,page_shell,labels):
 url=SITE+'/directory/'+slug+'/'
 checked_label=date.fromisoformat(row['checked']).strftime('%B %d, %Y').replace(' 0',' ')
 sections=''.join('<section><h2>'+e(s['heading'])+'</h2><p>'+e(s['text'])+'</p></section>' for s in row['editorial_sections'])
 address_label='Mailing address' if row['address_kind']=='mailing' else 'Published contact address'
 name=e(row['name']);website=e(row['website'],quote=True)
 body=f'''<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Business Directory</a><span>/</span><a href="/directory/{row['category']}/">{e(labels[row['category']])}</a></div>
<header class="page-head"><span class="page-eyebrow">Pittsburgh-area business directory</span><h1 class="page-title">{name}</h1><p class="page-deck">{e(row['city'])}, Pennsylvania · Official-source business profile</p><p>AI-assisted editorial profile by The Pittsburgh Wire editorial · Published and checked <time datetime="{row['checked']}">{checked_label}</time></p></header>
<main class="archive"><article class="official-profile">{sections}<section><h2>Published contact details</h2><dl><dt>Business</dt><dd>{name}</dd><dt>{address_label}</dt><dd>{e(row['address'])}</dd><dt>Telephone</dt><dd><a class="contact-link" href="tel:+1{''.join(c for c in row['phone'] if c.isdigit())}">{e(row['phone'])}</a></dd><dt>Official website and source</dt><dd><a class="contact-link" href="{website}" rel="noopener noreferrer">{name}: official information</a></dd></dl><p>Confirm appointments, service availability and the correct contact route directly. A published address is not evidence of public walk-in access.</p></section><section><h2>Source and editorial scope</h2><p>The official website linked above was reviewed {checked_label} for the service and contact information stated here. The editorial category, {e(labels[row['category']])}, groups related published activities. Buyer questions are preparation prompts, not findings about the provider. Inclusion is not a rating, endorsement, inspection or verification of insurance or credentials.</p></section><section><h2>Prepare your enquiry</h2><p><a href="/guides/business-service-planning/">Explore the business-service planning guides</a> for records to prepare and questions to ask. <a href="/directory/{row['category']}/">Browse {e(labels[row['category']].lower())}</a> or <a href="/directory/">search the full business directory</a>.</p></section></article></main>'''
 author={'@type':'Organization','@id':SITE+'/#editorial','name':'The Pittsburgh Wire editorial','url':SITE+'/about/'}
 entity={'@type':'Organization','@id':url+'#business','name':row['name'],'url':row['website'],'telephone':'+1'+''.join(c for c in row['phone'] if c.isdigit())}
 # A mailing address is correspondence information, not a Place or geo location.
 address={'@type':'PostalAddress','streetAddress':row['address'].split(', '+row['city'])[0],'addressLocality':row['city'],'addressRegion':'PA','addressCountry':'US','postalCode':re.search(r'\b\d{5}(?:-\d{4})?$',row['address']).group()}
 entity['address']=address
 graph=[author,entity,{'@type':'WebPage','@id':url+'#page','url':url,'name':row['name'],'datePublished':row['published'],'dateModified':row['checked'],'author':{'@id':author['@id']},'about':{'@id':entity['@id']},'citation':row['source']}]
 markup=page_shell(e(row['name']+' | Pittsburgh Business Directory | The Pittsburgh Wire'),e(row['description'],quote=True),url,body,active_nav='/directory/')
 markup=markup.replace('</head>',STYLE+'<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph}).replace('<','\\u003c')+'</script></head>')
 p=Path(root)/'directory'/slug/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(markup)
