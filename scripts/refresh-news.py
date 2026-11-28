"""Refresh news discovery surfaces during the production build."""
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_site import (
    build_category_pages, build_news_index, build_news_sitemap, scan_articles,
    update_homepage,
)

repo = str(ROOT)
articles = scan_articles(repo)
build_news_index(repo, articles)
list(build_category_pages(repo, articles))
update_homepage(repo, articles)
build_news_sitemap(repo, articles)

sitemap = ROOT / "sitemap.xml"
xml = sitemap.read_text(encoding="utf-8")
listed = set(re.findall(r"<loc>([^<]+)</loc>", xml))
entries = []
for article in articles:
    page = ROOT / "news" / article["slug"] / "index.html"
    html = page.read_text(encoding="utf-8")
    canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
    if canonical and 'name="robots" content="noindex' not in html:
        url = escape(canonical.group(1))
        if url not in listed:
            entries.append(f"  <url><loc>{url}</loc><lastmod>{article['date']}</lastmod></url>\n")
            listed.add(url)
sitemap.write_text(xml.replace("</urlset>", "".join(entries) + "</urlset>", 1), encoding="utf-8")
