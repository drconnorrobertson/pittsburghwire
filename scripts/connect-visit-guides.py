"""Connect existing educational visit guides from the established local-guide hub.

Run after other release generators. Preserve articles, canonicals and dates.
"""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


class Guide(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_heading = False
        self.canonical = ""
        self.robots = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.in_heading = True
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content", "")

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_heading = False

    def handle_data(self, data):
        if self.in_heading:
            self.title += data


def connect(root=ROOT):
    groups = json.loads((root / "data/visit-guide-collections.json").read_text())
    sections = []
    seen = set()
    for group in groups:
        links = []
        for slug in group["slugs"]:
            if not re.fullmatch(r"[a-z0-9-]+", slug) or slug in seen:
                raise ValueError("Invalid or repeated visit guide: " + slug)
            seen.add(slug)
            guide = Guide()
            guide.feed((root / "guides" / slug / "index.html").read_text())
            route = "/guides/" + slug + "/"
            if (not guide.title or "noindex" in guide.robots or
                    guide.canonical != "https://www.thepittsburghwire.com" + route):
                raise ValueError("Guide is not a public canonical owner: " + slug)
            links.append(f'<li><a href="{route}">{escape(guide.title)}</a></li>')
        sections.append(f'<section><h3>{escape(group["title"])}</h3>'
                        f'<p>{escape(group["intro"])}</p><ul>{"".join(links)}</ul></section>')
    block = ('<!-- visit-guide-collections:start -->'
             '<section aria-labelledby="visit-guide-collections">'
             '<h2 id="visit-guide-collections">Plan a visit or cultural outing</h2>'
             '<p>These independent educational guides help you prepare questions, '
             'read source material and organize a visit. Examples are fictional '
             'where labelled; use the linked operators for current arrangements.</p>'
             + "".join(sections) + '</section><!-- visit-guide-collections:end -->')
    target = root / "best/index.html"
    html = target.read_text()
    html = re.sub(r'<!-- visit-guide-collections:start -->[\s\S]*?<!-- visit-guide-collections:end -->', '', html)
    if html.count('</main>') != 1:
        raise ValueError("Expected one local-guide directory main element")
    target.write_text(html.replace('</main>', block + '</main>', 1))
    return len(seen)


if __name__ == "__main__":
    print(f"Connected {connect()} existing visit guides from the local-guide directory.")
