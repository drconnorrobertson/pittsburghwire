"""Archive elapsed notice windows without claiming the underlying closure ended."""
import json,re,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_site

def expired(slug,now=None):
    now=now or datetime.now(ZoneInfo('America/New_York'))
    value=json.loads((ROOT/'scripts/alert-expiry.json').read_text()).get(slug)
    return bool(value and now>=datetime.fromisoformat(value))

def apply():
    entries=json.loads((ROOT/'scripts/alert-expiry.json').read_text())
    now=datetime.now(ZoneInfo('America/New_York'))
    articles=build_site.scan_articles(str(ROOT))
    current=[a for a in articles if not expired(a['slug'],now)]
    if len(current)<3:raise ValueError('Too few current articles to refresh homepage')
    build_site.update_homepage(str(ROOT),current)
    for slug,end in entries.items():
        p=ROOT/'news'/slug/'index.html';t=p.read_text()
        t=re.sub(r'<!-- alert-status:start -->.*?<!-- alert-status:end -->','',t,flags=re.S)
        status='Coverage window ended' if expired(slug,now) else 'Time-sensitive notice'
        note=('This notice’s published coverage window has ended. It remains available as an archive; this does not establish that the road, trail or service is now operating normally. Check the linked operator for current conditions.' if expired(slug,now) else 'This notice describes a published date window. Confirm current conditions and instructions with the linked authority.')
        banner=f'<!-- alert-status:start --><aside class="article-deck" data-alert-expires="{end}"><strong>{status}.</strong> {note}</aside><!-- alert-status:end -->'
        t=re.sub(r'(<article class="article-body"[^>]*>)',lambda m:m[1]+banner,t,count=1)
        if not 'data-alert-expires' in t:raise ValueError('Missing article body: '+slug)
        if '/js/alert-expiry.js' not in t:t=t.replace('</body>','<script src="/js/alert-expiry.js?v=20261018" defer></script></body>')
        p.write_text(t)
    print('Notice windows checked; elapsed alerts removed from homepage promotion, all story pages retained.')
if __name__=='__main__':apply()
