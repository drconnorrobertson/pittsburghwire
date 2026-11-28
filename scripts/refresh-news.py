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
modified_dates = {}
for article in articles:
    page = ROOT / "news" / article["slug"] / "index.html"
    html = page.read_text(encoding="utf-8")
    canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
    if canonical and 'name="robots" content="noindex' not in html:
        url = escape(canonical.group(1))
        modified = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
        lastmod = max(article["date"], modified.group(1)) if modified else article["date"]
        modified_dates[url] = lastmod
        if url not in listed:
            entries.append(f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod></url>\n")
            listed.add(url)
def refresh_lastmod(match):
    entry = match.group()
    location = re.search(r"<loc>([^<]+)</loc>", entry)
    if not location or location.group(1) not in modified_dates:
        return entry
    previous = re.search(r"<lastmod>([^<]+)</lastmod>", entry)
    updated = modified_dates[location.group(1)]
    if previous:
        return entry if previous.group(1) >= updated else entry.replace(previous.group(), f"<lastmod>{updated}</lastmod>", 1)
    return entry.replace("</loc>", f"</loc><lastmod>{updated}</lastmod>", 1)


xml = re.sub(r"<url>.*?</url>", refresh_lastmod, xml, flags=re.S)
sitemap.write_text(xml.replace("</urlset>", "".join(entries) + "</urlset>", 1), encoding="utf-8")
