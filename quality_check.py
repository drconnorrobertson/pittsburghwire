"""Check public navigation, crawlability, and source status after a site build."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import xml.etree.ElementTree as ET

from directory_index import (ALIASES, CATEGORIES, INACTIVE, PENDING_REVIEW,
                             UNVERIFIED, VERIFIED, VERIFIED_CATEGORY)

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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
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
    for path in ROOT.rglob("*.html"):
        if "templates" in path.parts:
            continue
        try:
            page = parse(path)
            pages[path] = page
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
    print(f"Checked {len(pages)} pages, {links_checked} local links, {len(sitemap)} sitemap URLs; "
          f"{len(VERIFIED)} sourced profiles, {guide_count} curated guides, {len(errors)} errors")
    for error in errors[:30]:
        print("ERROR:", error)
    return not errors


if __name__ == "__main__":
    raise SystemExit(0 if check() else 1)
