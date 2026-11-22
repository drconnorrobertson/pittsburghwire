"""Select an existing editorial feature from the actual full catalog renderer."""
from pathlib import Path
import argparse,shutil,sys,tempfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import business_catalog,build_site
parser=argparse.ArgumentParser();parser.add_argument('slug');args=parser.parse_args();slug=args.slug
assert slug in business_catalog.DATA and slug in business_catalog.FEATURES
with tempfile.TemporaryDirectory(prefix='wire-feature-render-')as name:
 out=Path(name);shutil.copytree(ROOT,out,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','__pycache__'))
 business_catalog.write(out,build_site.page_shell)
 target=Path('directory')/slug/'index.html';shutil.copyfile(out/target,ROOT/target)
url=business_catalog.SITE+'/directory/'+slug+'/'
for path in ['sitemap.xml','directory-sitemap.xml']:
 p=ROOT/path;s=p.read_text();root=ET.fromstring(s)
 matches=[e for e in root if e.find('{*}loc')is not None and e.find('{*}loc').text==url];assert len(matches)==1,(path,len(matches))
 # Keep every other byte and date unchanged in the published sitemap.
 import re
 pattern=r'(<url>\s*<loc>'+re.escape(url)+r'</loc>[\s\S]*?<lastmod>)[^<]+(</lastmod>)'
 changed,n=re.subn(pattern,lambda m:m.group(1)+business_catalog.DATA[slug]['checked']+m.group(2),s,count=1);assert n==1,path;p.write_text(changed)
print('Rendered existing feature profile and updated its two sitemap dates:',slug)
