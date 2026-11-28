"""Publish a county directory and jurisdiction references from county GIS data."""
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build_site import page_shell
from service_buying_guides import STYLE

SITE = "https://www.thepittsburghwire.com"
HUB = "/municipalities/"
COUNTY = "https://apps.alleghenycounty.us/website/"
BOUNDARIES = "https://data.wprdc.org/dataset/allegheny-county-municipal-boundaries"
ADDRESS = ("https://www.alleghenycounty.us/Government/Department-Directory/"
           "Information-Technology/Address-Management/Municipal-Information")
EXISTING = {"city-of-pittsburgh": "/neighborhoods#all-city-neighborhoods",
            "homestead-borough": "/neighborhoods/homestead/"}
MATCHED_NAMES = {
    "baldwin-borough": "baldwin-township",
    "baldwin-township": "baldwin-borough",
    "elizabeth-borough": "elizabeth-township",
    "elizabeth-township": "elizabeth-borough",
    "springdale-borough": "springdale-township",
    "springdale-township": "springdale-borough",
    "mount-oliver-borough": "/neighborhoods/mt-oliver/",
}


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def write(route, title, description, content):
    body = f'''<div class="breadcrumb">{link("/", "Home")}<span>/</span>{link(HUB, "Allegheny County municipalities")}</div>
<header class="page-head"><h1 class="page-title">{escape(title)}</h1><p class="page-deck">{escape(description)}</p></header>
<main class="archive"><article class="service-guide">{content}</article></main>'''
    page = page_shell(escape(title + " | The Pittsburgh Wire"), escape(description), SITE + route, body)
    path = ROOT / route.strip("/") / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page.replace("</head>", STYLE + "</head>", 1))


def publish():
    items = json.loads((ROOT / "data/allegheny-municipalities.json").read_text())
    by_slug = {item["slug"]: item for item in items}
    if len(by_slug) != 130 or len({item["id"] for item in items}) != 130:
        raise ValueError("Expected 130 unique municipal records")
    routes = [HUB]
    directory = []
    for item in items:
        slug, name = item["slug"], item["name"]
        route = HUB + slug + "/"
        directory.append(f'<li>{link(route, name)}</li>')
        routes.append(route)
        edges = [link(HUB + adj + "/", by_slug[adj]["name"]) for adj in item["adjacent"]]
        profile = link(f'{COUNTY}MuniProfile.asp?muni={item["id"]}', f"Allegheny County profile for {name}")
        area = f'<p>County GIS reports a mapped area of {item["area"]:.2f} square miles.</p>' if item["area"] is not None else ""
        municipal_note = "<p>This municipality extends outside Allegheny County. Confirm the county for the exact address before using county-specific services.</p>" if slug in {"mcdonald-borough", "trafford-borough"} else ""
        similar = MATCHED_NAMES.get(slug)
        if similar and similar.startswith("/"):
            municipal_note += f'<p>Also see {link(similar, "the City of Pittsburgh’s Mt. Oliver neighborhood")}, which is a separate jurisdiction.</p>'
        elif similar:
            municipal_note += f'<p>Checking an address with the same place name? Compare it with {link(HUB + similar + "/", by_slug[similar]["name"])}.</p>'
        boundaries = '<section><h2>Municipal boundaries</h2>' + area
        if edges:
            boundaries += '<p>Allegheny County municipalities that share a mapped border include ' + ", ".join(edges) + '.</p>'
        boundaries += f'<p>{link(BOUNDARIES, "Open the county’s municipal GIS dataset")}.</p></section>'
        details = f'<section><h2>Find the right local office</h2><p>Start with the {profile}. For a property or service question, confirm the municipality by street address before contacting a local office. A postal city name can cover addresses in multiple municipalities.</p>{municipal_note}<p>{link(ADDRESS, "County address and municipality resources")}</p></section>'
        if slug == "carnegie-borough":
            details += '<p>Transit coverage: <a href="/news/carnegie-station-prt-public-meeting-december-1-2026">PRT’s Carnegie Station and park-and-ride plans</a>.</p>'
        if slug in EXISTING:
            details += f'<p>{link(EXISTING[slug], f"Explore the Wire’s local coverage of {name}")}.</p>'
        write(route, f"{name}, Pennsylvania", f"Find the Allegheny County profile for {name}, see bordering municipalities, and check jurisdiction by address.", details + boundaries)
    write(HUB, "Allegheny County Municipalities", "Find all 130 cities, boroughs, towns, and townships in Allegheny County and check which jurisdiction serves an address.",
          '<ul>' + "".join(directory) + f'</ul><p>{link(COUNTY + "MuniList.asp", "Source: Allegheny County municipality list")}.</p>')
    index = ROOT / "neighborhoods/index.html"
    page = index.read_text()
    marker = '<h2>All 90 Pittsburgh city neighborhoods</h2>'
    discovery = f'<p>Looking outside city limits? Browse {link(HUB, "all 130 Allegheny County municipalities")}.</p>'
    if discovery not in page:
        if page.count(marker) != 1:
            raise ValueError("City neighborhood index heading is missing")
        index.write_text(page.replace(marker, marker + discovery, 1))
    sitemap = ROOT / "sitemap.xml"
    xml = sitemap.read_text()
    missing = [f'  <url><loc>{SITE}{route}</loc></url>\n' for route in routes if f'<loc>{SITE}{route}</loc>' not in xml]
    sitemap.write_text(xml.replace("</urlset>", "".join(missing) + "</urlset>", 1))
    print(f"Published {len(items)} municipality references and the county index.")


if __name__ == "__main__":
    publish()
