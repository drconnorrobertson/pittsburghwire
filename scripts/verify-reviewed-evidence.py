"""Check relationship provenance and rejection controls against rendered profiles."""
from pathlib import Path
from copy import deepcopy
import json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catalog_evidence import evidence_errors,reviewed_links_markup
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/businesses.json').read_text());slugs=[slug for slug,row in d.items() if row.get('official_research',{}).get('evidence_model')=='reviewed_links_v1']
for slug in slugs:
 row=d[slug];research=row['official_research'];html=(ROOT/'directory'/slug/'index.html').read_text();assert reviewed_links_markup(row)in html
 assert 'These official links were checked on'not in html
 assert 'AI-assisted profile by <a href="/about">The Pittsburgh Wire editorial</a>'in html
 graph=json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)[-1])['@graph'];web=next(x for x in graph if x.get('@type')=='WebPage')
 assert web['datePublished']==row['published'] and web['dateModified']==row['checked']
 assert web['author']['@id'].endswith('/#editorial')
 for link in research['links'].values():assert not evidence_errors(research,link),(slug,link)
r=d['bar-marco']['official_research'];link=r['links']['contact'];negative=[]
for key,value in [('relationship','trusted_host'),('target','https://www.exploretock.com/some-other-restaurant'),('source','https://unrelated.example/'),('checked',''),('note','')]:
 bad=deepcopy(link);bad['evidence'][key]=value;assert evidence_errors(r,bad),key;negative.append(key)
bad=deepcopy(link);del bad['evidence'];assert evidence_errors(r,bad);negative.append('missing evidence')
r=d['commonplace-coffee-northland-library']['official_research'];bad=deepcopy(r['links']['about']);bad['evidence']['business_url']='https://commonplacecoffee.com/other-location';assert evidence_errors(r,bad);negative.append('wrong host-venue business')
# Unreviewed external links still fail; adding provenance to one page never trusts a host globally.
r=deepcopy(d['bar-marco']['official_research']);r.pop('evidence_model');assert evidence_errors(r,link);negative.append('unreviewed external link')
print(json.dumps({'reviewedProfiles':len(slugs),'negativeControls':negative,'scope':'Exact destinations and relationship evidence, original publication dates, explicit source labels and editorial attribution.'}))
