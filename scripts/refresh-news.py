"""Refresh news discovery surfaces during the production build."""
import re
import sys
from datetime import date
from email.utils import formatdate
from calendar import timegm
from xml.etree import ElementTree as ET
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
archive = Path(build_news_index(repo, articles))
list(build_category_pages(repo, articles))
update_homepage(repo, articles)
build_news_sitemap(repo, articles)

sitemap = ROOT / "sitemap.xml"
xml = sitemap.read_text(encoding="utf-8")
listed = set(re.findall(r"<loc>([^<]+)</loc>", xml))
entries = []
modified_dates = {}
feed_items = []
for article in articles:
    page = ROOT / "news" / article["slug"] / "index.html"
    html = page.read_text(encoding="utf-8")
    canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
    if canonical and 'name="robots" content="noindex' not in html:
        if len(feed_items) < 30:
            feed_items.append((canonical.group(1), article))
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

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
site = "https://www.thepittsburghwire.com"
ET.SubElement(channel, "title").text = "The Pittsburgh Wire"
ET.SubElement(channel, "link").text = site + "/news"
ET.SubElement(channel, "description").text = "Local news from Pittsburgh and Allegheny County."
ET.SubElement(channel, "language").text = "en-us"
seen = set()
for url, article in feed_items:
    if url in seen:
        continue
    seen.add(url)
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = article["title"]
    ET.SubElement(item, "link").text = url
    ET.SubElement(item, "guid", isPermaLink="true").text = url
    ET.SubElement(item, "description").text = article["desc"]
    published = date.fromisoformat(article["date"])
    ET.SubElement(item, "pubDate").text = formatdate(timegm(published.timetuple()), usegmt=True)
ET.ElementTree(rss).write(ROOT / "news-rss.xml", encoding="utf-8", xml_declaration=True)

archive_html = archive.read_text(encoding="utf-8")
archive_html = archive_html.replace(
    "</head>",
    '  <link rel="alternate" type="application/rss+xml" title="The Pittsburgh Wire News" href="/news-rss.xml" />\n</head>',
    1,
)
archive_html = archive_html.replace(
    '<p class="page-count">',
    '<p><a href="/news-rss.xml">Subscribe via RSS</a></p>\n    <p class="page-count">',
    1,
)
archive.write_text(archive_html, encoding="utf-8")
