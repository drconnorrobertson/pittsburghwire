"""Check public navigation, crawlability, and source status after a site build."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from directory_index import (ALIASES, CATEGORIES, INACTIVE, PENDING_REVIEW,
                             UNVERIFIED, VERIFIED, VERIFIED_CATEGORY)
from build_site import WITHDRAWN_NEWS
from neighborhood_hubs import LOCAL_PROFILES

ROOT = Path(__file__).resolve().parent
SITE = "https://www.thepittsburghwire.com"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.robots = ""
        self.links = []
        self.jsonld = []
        self._json = None
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._json = ""

    def handle_data(self, data):
        if self._json is not None:
            self._json += data

    def handle_endtag(self, tag):
        if tag == "script" and self._json is not None:
            self.jsonld.append(json.loads(self._json))
            self._json = None


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def check():
    errors = []
    pages = {}
    links_checked = 0
    schema_urls_checked = 0

    def strings(value):
        if isinstance(value, dict):
            for child in value.values():
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)
        elif isinstance(value, str):
            yield value

    for path in ROOT.rglob("*.html"):
        if "templates" in path.parts:
            continue
        if path.name.startswith("google") and path.parent == ROOT:
            continue
        try:
            page = parse(path)
            pages[path] = page
            if page.h1_count != 1:
                errors.append(f"Expected one H1 in {path.relative_to(ROOT)}, found {page.h1_count}")
            for obj in page.jsonld:
                if isinstance(obj, dict) and obj.get("@type") == "NewsArticle":
                    for field in ("headline", "description"):
                        value = obj.get(field, "")
                        if isinstance(value, str) and html.unescape(value) != value:
                            errors.append(f"Encoded structured-data {field}: {path.relative_to(ROOT)}")
                    content = path.read_text(encoding="utf-8")
                    byline = re.search(r'class="article-byline"[^>]*>\s*By\s*(?:<a[^>]*>)?([^<]+)', content, re.S)
                    if byline:
                        visible = " ".join(html.unescape(byline.group(1)).replace("\xa0", " ").split())
                        visible = re.split(r'\s*[|—]\s*|,', visible)[0].strip()
                        author = obj.get("author")
                        if not isinstance(author, dict) or author.get("name") != visible:
                            errors.append(f"Article byline and structured-data author differ: {path.relative_to(ROOT)}")
                for url in strings(obj):
                    parsed = urlsplit(url)
                    if parsed.netloc != "www.thepittsburghwire.com" or not parsed.path:
                        continue
                    schema_urls_checked += 1
                    local = ROOT / unquote(parsed.path).lstrip("/")
                    if not (local.is_file() or (local / "index.html").is_file()):
                        errors.append(f"Broken structured-data URL {path.relative_to(ROOT)} -> {url}")
            for href in page.links:
                if not href.startswith("/") or href.startswith("//"):
                    continue
                links_checked += 1
                local = ROOT / unquote(urlsplit(href).path).lstrip("/")
                if not (local.is_file() or (local / "index.html").is_file() or
                        (ROOT / (unquote(urlsplit(href).path).lstrip("/") + ".html")).is_file()):
                    errors.append(f"Broken link {path.relative_to(ROOT)} -> {href}")
        except Exception as exc:
            errors.append(f"Invalid page {path.relative_to(ROOT)}: {exc}")

    sitemap = [entry.find("{*}loc").text for entry in ET.parse(ROOT / "sitemap.xml").getroot()]
    if len(sitemap) != len(set(sitemap)):
        errors.append("Duplicate sitemap URLs")
    for url in sitemap:
        relative = urlsplit(url).path.strip("/")
        path = ROOT / relative / "index.html" if relative else ROOT / "index.html"
        page = pages.get(path)
        if not page or page.canonical != url or "noindex" in page.robots:
            errors.append(f"Sitemap URL mismatches page: {url}")

    news_root = ET.parse(ROOT / "news-sitemap.xml").getroot()
    recent = set()
    for entry in news_root:
        url = entry.find("{*}loc").text
        published = entry.find("{*}news/{*}publication_date")
        if published is None or not date.today() - timedelta(days=1) <= date.fromisoformat(published.text) <= date.today():
            errors.append(f"Stale or missing news sitemap date: {url}")
        if url not in sitemap or url in recent:
            errors.append(f"Invalid news sitemap URL: {url}")
        recent.add(url)

    for page_path in sorted((ROOT / "neighborhoods").glob("*/index.html")):
        source = page_path.read_text(encoding="utf-8")
        news_cards = re.findall(r'<a href="/news/([^"/]+)" class="article-card">', source)
        business_cards = re.findall(r'<a href="/directory/([^"/]+)" class="biz-card">', source)
        if set(business_cards) != set(LOCAL_PROFILES.get(page_path.parent.name, ())):
            errors.append(f"Neighborhood business mapping drift: {page_path.relative_to(ROOT)}")
        for slug in news_cards:
            article_path = ROOT / "news" / slug / "index.html"
            if article_path not in pages or "noindex" in pages[article_path].robots:
                errors.append(f"Neighborhood promotes unavailable article: {page_path.relative_to(ROOT)} -> {slug}")
        for slug in business_cards:
            profile_path = ROOT / "directory" / slug / "index.html"
            if slug not in VERIFIED or profile_path not in pages or "noindex" in pages[profile_path].robots:
                errors.append(f"Neighborhood promotes unverified profile: {page_path.relative_to(ROOT)} -> {slug}")
        counts = re.findall(r'<span class="section-label-count">(\d+) (?:Articles?|Business(?:es)?)</span>', source)
        if len(counts) < 2 or [int(n) for n in counts[:2]] != [len(news_cards), len(business_cards)]:
            errors.append(f"Neighborhood card counts drift: {page_path.relative_to(ROOT)}")

    for withdrawn_article in ("pittsburgh-ranked-top-city-small-business-growth", *WITHDRAWN_NEWS):
        withdrawn_path = ROOT / "news" / withdrawn_article / "index.html"
        if "noindex" not in pages[withdrawn_path].robots:
            errors.append(f"Unsupported article is indexable: {withdrawn_article}")
        if any(withdrawn_article in url for url in sitemap):
            errors.append(f"Unsupported article appears in sitemap: {withdrawn_article}")
        for path, page in pages.items():
            if path != withdrawn_path and any(withdrawn_article in href for href in page.links):
                errors.append(f"Unsupported article promoted by {path.relative_to(ROOT)}")

    hub = (ROOT / "directory" / "index.html").read_text(encoding="utf-8")
    for slug in VERIFIED:
        path = ROOT / "directory" / slug / "index.html"
        if path not in pages or "noindex" in pages[path].robots:
            errors.append(f"Verified profile unavailable: {slug}")
        if f'/directory/{slug}/' not in hub or f"{SITE}/directory/{slug}/" not in sitemap:
            errors.append(f"Verified profile not discoverable: {slug}")
        category = ROOT / "directory" / VERIFIED_CATEGORY[slug] / "index.html"
        if f'/directory/{slug}/' not in category.read_text(encoding="utf-8"):
            errors.append(f"Verified profile absent from category: {slug}")
    withheld = PENDING_REVIEW | UNVERIFIED | INACTIVE | set(ALIASES)
    for slug in withheld:
        if f'/directory/{slug}/' in hub or f"{SITE}/directory/{slug}/" in sitemap:
            errors.append(f"Withheld directory profile promoted: {slug}")
        if slug in PENDING_REVIEW | UNVERIFIED | INACTIVE:
            path = ROOT / "directory" / slug / "index.html"
            if "noindex" not in pages[path].robots:
                errors.append(f"Withheld directory profile indexable: {slug}")
    guide_count = 0
    for path in (ROOT / "best").glob("*/index.html"):
        content = path.read_text(encoding="utf-8")
        if 'name="wire:curated-guide" content="true"' in content:
            guide_count += 1
            if "noindex" in pages[path].robots or pages[path].canonical not in sitemap:
                errors.append(f"Curated guide not discoverable: {path.parent.name}")
        elif "noindex" not in pages[path].robots or "This guide is not available." not in content:
            errors.append(f"Unresearched guide still published: {path.parent.name}")
    print(f"Checked {len(pages)} pages, {links_checked} local links, {schema_urls_checked} structured-data URLs, {len(sitemap)} sitemap URLs; "
          f"{len(VERIFIED)} sourced profiles, {guide_count} curated guides, {len(errors)} errors")
    for error in errors[:30]:
        print("ERROR:", error)
    return not errors


if __name__ == "__main__":
    raise SystemExit(0 if check() else 1)
