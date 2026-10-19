"""Link to each article's declared canonical, preserving existing URL ownership.

Run last in the deployment build, after the other generators. This does not
change article canonicals, publication dates, content or indexability.
"""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.thepittsburghwire.com"


class Metadata(HTMLParser):
    canonical = ""
    robots = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")


def normalize(root=ROOT):
    owners = {}
    for page in (root / "news").glob("*/index.html"):
        meta = Metadata()
        meta.feed(page.read_text())
        target = urlsplit(meta.canonical)
        if "noindex" in meta.robots or target.netloc != urlsplit(SITE).netloc:
            continue
        source = "/news/" + page.parent.name
        for alias in (source, source + "/", source + "/index.html"):
            owners[alias] = target.path

    count = 0
    for page in root.rglob("*.html"):
        if "templates" in page.relative_to(root).parts:
            continue
        text = page.read_text()

        def replace(match):
            original = unescape(match[2])
            url = urlsplit(original)
            if url.netloc and url.netloc != urlsplit(SITE).netloc:
                return match[0]
            if url.scheme and url.scheme not in ("http", "https"):
                return match[0]
            target = owners.get(url.path)
            if not target or target == url.path:
                return match[0]
            updated = urlunsplit((url.scheme, url.netloc, target, url.query, url.fragment))
            return "href=" + match[1] + escape(updated, quote=True) + match[1]

        updated = re.sub(r'''href=(["'])(.*?)\1''', replace, text)
        if updated != text:
            page.write_text(updated)
            count += 1
    print(f"Normalized canonical news links in {count} pages.")


if __name__ == "__main__":
    normalize()
