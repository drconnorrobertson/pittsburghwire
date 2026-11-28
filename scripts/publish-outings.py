"""Build the Pittsburgh outing collections from editorially selected visit guides."""
import json
import re
import sys
from html import escape
from pathlib import Path

from importlib import import_module

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build_site import page_shell
from service_buying_guides import STYLE

Guide = import_module("connect-visit-guides").Guide
SITE = "https://www.thepittsburghwire.com"
HUB = "/best/things-to-do/itineraries/"
PARENT = "/best/things-to-do/"
WEEKEND = PARENT + "this-weekend/"


def link(route, label):
    return f'<a href="{escape(route, quote=True)}">{escape(label)}</a>'


def write_page(route, title, description, content, parent, parent_title):
    body = f'''<div class="breadcrumb">{link("/", "Home")}<span>/</span>{link(parent, parent_title)}</div>
<header class="page-head"><h1 class="page-title">{escape(title)}</h1>
<p class="page-deck">{escape(description)}</p></header>
<main class="archive"><div class="service-guide">{content}</div></main>'''
    page = page_shell(escape(title + " | The Pittsburgh Wire"), escape(description),
                      SITE + route, body, active_nav="/best/")
    path = ROOT / route.strip("/") / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page.replace("</head>", STYLE + "</head>", 1))


def visit_target(target):
    route = target if target.startswith("/") else f"/guides/{target}/"
    parser = Guide()
    parser.feed((ROOT / route.strip("/") / "index.html").read_text())
    if not parser.title or parser.canonical != SITE + route or "noindex" in parser.robots.lower():
        raise ValueError(f"Expected an indexable canonical visit guide at {route}")
    return route, parser.title.strip()


def add_discovery(path, content):
    page = path.read_text()
    page = re.sub(r'<!-- outing-collections:start -->.*?<!-- outing-collections:end -->\n?',
                  "", page, flags=re.S)
    if page.count("</main>") != 1:
        raise ValueError(f"Expected one main element in {path}")
    block = '<!-- outing-collections:start -->' + content + '<!-- outing-collections:end -->\n'
    path.write_text(page.replace("</main>", block + "</main>", 1))


def publish():
    outings = json.loads((ROOT / "data/pittsburgh-outings.json").read_text())
    links = []
    routes = [HUB]
    for outing in outings:
        slug, title, description = (outing[key] for key in ("slug", "title", "description"))
        route = HUB + slug + "/"
        stops = outing["stops"]
        if not re.fullmatch(r"[a-z0-9-]+", slug) or route in routes or len(stops) < 2:
            raise ValueError(f"Invalid or repeated itinerary: {slug}")
        routes.append(route)
        items = []
        for target, advice in stops:
            href, label = visit_target(target)
            items.append(f'<li><p>{escape(advice)}</p><p>{link(href, label)}</p></li>')
        content = '<h2>Plan your stops</h2><ol>' + "".join(items) + '</ol>'
        content += f'<p>For dated events, see {link(WEEKEND, "the Pittsburgh weekend guide")}.</p>'
        write_page(route, title, description, content, HUB, "Pittsburgh itineraries")
        links.append(f'<li><h2>{link(route, title)}</h2><p>{escape(description)}</p></li>')
    write_page(HUB, "Pittsburgh Itineraries and Day Outings",
               "Plan a Pittsburgh day by neighborhood or interest, from museums and family outings to architecture, gardens and riverfront rides.",
               '<ul>' + "".join(links) + '</ul>', PARENT, "Things to Do")
    for route in (PARENT, WEEKEND, "/best/"):
        add_discovery(ROOT / route.strip("/") / "index.html",
                      f'<section><h2 class="month-head">Plan a Pittsburgh outing</h2><p>{link(HUB, "Find a Pittsburgh itinerary by place or interest")}.</p></section>')
    sitemap = ROOT / "sitemap.xml"
    xml = sitemap.read_text()
    for route in routes:
        loc = f"<loc>{SITE}{route}</loc>"
        if loc not in xml:
            xml = xml.replace("</urlset>", f"  <url>{loc}</url>\n</urlset>", 1)
    sitemap.write_text(xml)
    return len(outings)


if __name__ == "__main__":
    print(f"Published {publish()} Pittsburgh itineraries.")
