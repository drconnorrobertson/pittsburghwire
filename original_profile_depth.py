"""Extend the earlier source-checked profiles without changing their historical facts."""
import json,re
from pathlib import Path
from html import escape
from business_depth import profile_depth
from business_catalog import DATA,AUTHOR,SITE,schema

def write(repo):
 root=Path(repo);path=root/'data/original-businesses.json'
 if not path.exists():return 0
 rows=json.loads(path.read_text());allrows={**DATA,**rows}
 for slug,row in rows.items():
  p=root/'directory'/slug/'index.html';markup=p.read_text()
  markup=re.sub(r'\s*<!-- ORIGINAL_DEPTH_START -->.*?<!-- ORIGINAL_DEPTH_END -->','',markup,flags=re.S)
  detail=row.get('official_research',{})
  quote=''
  if detail.get('status')=='corroborated' and detail.get('description_excerpt'):
   quote=f'<h2>From the official website</h2><p><a href="{escape(detail["url"],quote=True)}" rel="noopener noreferrer">{escape(row["name"])}’s official website</a> describes the business this way:</p><blockquote>{escape(detail["description_excerpt"])}</blockquote>'
  block=f'<!-- ORIGINAL_DEPTH_START --><section><h2>Directory guide for {escape(row["name"])}</h2><p>By <a href="/founder/" rel="author">Dr. Connor Robertson</a> · Directory guide updated October 7, 2026.</p>{quote}{profile_depth(row,allrows)}<p><a href="/directory/">Explore the complete Pittsburgh Wire business directory</a>.</p></section><!-- ORIGINAL_DEPTH_END -->'
  marker='</article>' if '<article class="profile-body">' in markup else '</main>'
  markup=markup.replace(marker,block+marker,1)
  marker='<!-- ORIGINAL_AUTHOR_SCHEMA -->'
  markup=re.sub(r'\s*'+re.escape(marker)+r'<script type="application/ld\+json">.*?</script>\s*','',markup,flags=re.S)
  graph=[AUTHOR,{'@type':'WebPage','@id':SITE+'/directory/'+slug+'/#page','url':SITE+'/directory/'+slug+'/','name':row['name'],'dateModified':'2026-10-07','author':{'@id':AUTHOR['@id']}}]
  markup=markup.replace('</head>',marker+schema(graph)+'\n</head>',1);p.write_text(markup)
 return len(rows)
