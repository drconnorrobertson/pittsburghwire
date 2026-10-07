"""Submit crawlable sitemap URLs to IndexNow after confirming the static deploy."""
import argparse, hashlib, json, time, urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
HOST='www.thepittsburghwire.com'
KEY='821bfb7d39db5d7a6ea1b5d0aa7ebd61'
def request(url,data=None):
    headers={'User-Agent':'PittsburghWireIndexing/1.0','Cache-Control':'no-cache'}
    if data is not None:headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers),timeout=30) as response:
        return response.status,response.read()
def main():
    p=argparse.ArgumentParser();p.add_argument('--wait-for-deploy',action='store_true');p.add_argument('--sitemap',default='sitemap.xml');p.add_argument('--verify-files',nargs='*',default=[]);args=p.parse_args()
    urls=list(dict.fromkeys(n.text for n in ET.parse(ROOT/args.sitemap).findall('.//{*}loc')))
    assert urls and all(u.startswith('https://'+HOST+'/') for u in urls)
    keyurl=f'https://{HOST}/{KEY}.txt'
    _,body=request(keyurl)
    if body.decode().strip()!=KEY:raise RuntimeError('Live IndexNow key file failed validation')
    files=args.verify_files or ['directory/index.html','directory-sitemap.xml']
    attempts=30 if args.wait_for_deploy else 1
    for attempt in range(attempts):
        failures=[]
        for f in files:
            path=ROOT/f
            if not path.is_file():continue
            route=f[:-len('index.html')] if f.endswith('index.html') else f
            try:
                _,body=request('https://'+HOST+'/'+route)
                if hashlib.sha256(body).digest()!=hashlib.sha256(path.read_bytes()).digest():failures.append(route)
            except Exception:failures.append(route)
        if not failures:break
        if attempt==attempts-1:raise RuntimeError('Deployment verification failed: '+', '.join(failures))
        print('Waiting for deployment',attempt+1,flush=True);time.sleep(20)
    results=[]
    for start in range(0,len(urls),10000):
        batch=urls[start:start+10000]
        status,body=request('https://api.indexnow.org/indexnow',json.dumps({'host':HOST,'key':KEY,'keyLocation':keyurl,'urlList':batch}).encode())
        if status not in (200,202):raise RuntimeError(f'IndexNow rejected batch: HTTP {status}')
        results.append({'urls':len(batch),'status':status,'response':body.decode()[:500]})
    print(json.dumps({'submitted':len(urls),'key_verified':True,'deployment_verified':True,'results':results,'note':'Submission is a crawl notification, not confirmation of indexing.'},indent=2))
if __name__=='__main__':main()
