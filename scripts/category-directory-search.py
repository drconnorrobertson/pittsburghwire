"""Add local category search without changing directory inventory or URL owners."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from collections import defaultdict
import json,re
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.h1=False;self.title=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h1':self.h1=True
  if tag=='a' and 'biz-card' in a.get('class','').split():self.cards.append(a.get('href'))
 def handle_endtag(self,tag):
  if tag=='h1':self.h1=False
 def handle_data(self,text):
  if self.h1:self.title+=text
rows=defaultdict(list)
for record in json.loads((ROOT/'data/directory-search.json').read_text()):rows[record['category']].append(record['url'])
start='<!-- category-search:start -->';end='<!-- category-search:end -->'
for category,urls in sorted(rows.items()):
 p=ROOT/'directory'/category/'index.html';s=p.read_text();parsed=Page();parsed.feed(s)
 assert len(parsed.cards)==len(urls) and set(parsed.cards)==set(urls),(category,'Category membership mismatch')
 s=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',s,flags=re.S)
 style='<style id="category-search-style">#category-search-controls{margin:24px 0}#category-search-controls[hidden],#category-search-empty[hidden],#category-directory-results .biz-card[hidden]{display:none!important}.category-search-row{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}.category-search-row input{min-width:0;flex:1 1 240px;font:inherit;font-size:16px;padding:12px;border:1px solid var(--rule)}.category-search-row button{font:inherit;min-height:44px;padding:10px 16px}#category-search-count{margin:12px 0}</style>'
 s=re.sub(r'<style id="category-search-style">.*?</style>','',s,flags=re.S)
 s=re.sub(r'<script defer src="/js/category-directory-search.js[^\"]*"></script>','',s)
 s=s.replace('</head>',style+'<script defer src="/js/category-directory-search.js?v=20261122"></script></head>')
 s=s.replace('id="category-directory-results" ','')
 m=re.search(r'<div\b[^>]*class="biz-grid"[^>]*>',s);assert m,category
 controls=start+'<div id="category-search-controls" hidden><label for="category-search">Search within '+escape(parsed.title.strip())+'</label><div class="category-search-row"><input id="category-search" type="search" placeholder="Name, address or service" aria-controls="category-directory-results"><button id="category-search-clear" type="button" disabled>Clear search</button></div><p id="category-search-count" role="status" aria-live="polite">'+str(len(urls))+' profiles in this category</p><p id="category-search-empty" hidden>No matching profiles. Clear the search or try fewer words.</p></div>'+end
 s=s[:m.start()]+controls+m[0].replace('<div ','<div id="category-directory-results" ',1)+s[m.end():];p.write_text(s)
print('Added category search to',len(rows),'collections;',sum(map(len,rows.values())),'profile links preserved.')
