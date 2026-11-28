"""Publish the City of Pittsburgh GIS neighborhood reference.

Boundary data and area estimates: City of Pittsburgh via WPRDC (CC BY).
Population estimates: University of Pittsburgh UCSUR via WPRDC, 2018–2022 ACS.
The committed data contains simplified drawing paths and exact-name ACS matches.
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build_site import page_shell

SITE = "https://www.thepittsburghwire.com"
INDEX = "/neighborhoods"
BOUNDARIES = "https://data.wprdc.org/dataset/neighborhoods2"
ACS = "https://data.wprdc.org/dataset/ucsur_neighborhoodprofiles_2024"
SNAPSHOTS = "https://engage.pittsburghpa.gov/neighborhood-snapshots"
WARDS = "https://www.pittsburghpa.gov/City-Government/The-City-Council/Neighborhoods-Wards"
STYLE = """<style>
.city-reference{max-width:850px;margin:2rem auto;padding:0 1.5rem;line-height:1.65}
.city-reference h2{margin:1.5rem 0 .5rem}
.city-reference a{text-decoration:underline}
.city-reference ul{padding-left:1.4rem}
.city-reference figure{margin:1rem 0}
.city-reference svg{display:block;width:100%;height:clamp(235px,43vw,395px);background:#faf7ef;border:1px solid #c8bfad}
.city-reference dl{display:flex;gap:1rem 2rem;flex-wrap:wrap;margin:1rem 0}
.city-reference dt{font-weight:bold}
.city-reference dd{margin:0}
.city-neighborhood-list{columns:3 200px;column-gap:2rem}
.city-neighborhood-list li{break-inside:avoid}
</style>"""
REGIONAL_GUIDES = {
    "East Liberty": ("/news/negley-avenue-safety-project-east-liberty", "Negley Avenue safety project"),
    "West End": ("/news/wabash-tunnel-closure-proposal-prt-board-october-23-2026", "Wabash Tunnel closure and park-and-ride access"),
    "Banksville": ("/news/1070-banksville-avenue-rezoning-hearing-november-30-2026", "1070 Banksville Avenue rezoning"),
    "Larimer": ("/news/larimer-housing-initiative-pittsburgh-2026", "Larimer housing and Mayflower Street"),
    "Central Lawrenceville": ("/neighborhoods/lawrenceville/", "Lawrenceville"),
    "Lower Lawrenceville": ("/neighborhoods/lawrenceville/", "Lawrenceville"),
    "Upper Lawrenceville": ("/neighborhoods/lawrenceville/", "Lawrenceville"),
    "Central Oakland": ("/neighborhoods/oakland/", "Oakland"),
    "North Oakland": ("/neighborhoods/oakland/", "Oakland"),
    "South Oakland": ("/neighborhoods/oakland/", "Oakland"),
    "West Oakland": ("/neighborhoods/oakland/", "Oakland"),
    "Squirrel Hill North": ("/neighborhoods/squirrel-hill/", "Squirrel Hill"),
    "Squirrel Hill South": ("/neighborhoods/squirrel-hill/", "Squirrel Hill"),
    "South Side Flats": ("/neighborhoods/south-side/", "South Side"),
    "South Side Slopes": ("/neighborhoods/south-side/", "South Side"),
    "Crawford-Roberts": ("/neighborhoods/hill-district/", "Hill District"),
    "Middle Hill": ("/neighborhoods/hill-district/", "Hill District"),
    "Upper Hill": ("/neighborhoods/hill-district/", "Hill District"),
    "Bedford Dwellings": ("/neighborhoods/hill-district/", "Hill District"),
    "Terrace Village": ("/neighborhoods/hill-district/", "Hill District"),
    "Hazelwood": ("/neighborhoods/hazelwood-green/", "Hazelwood Green development"),
    "Central Northside": ("/neighborhoods/north-side/", "North Side"),
    "North Shore": ("/neighborhoods/north-side/", "North Side"),
    "Allegheny Center": ("/neighborhoods/north-side/", "North Side"),
}


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def route(slug):
    return f"/neighborhoods/{slug}/"


def inject(path, markup):
    page = path.read_text()
    page = re.sub(r"<!-- city-neighborhood-reference:start -->.*?<!-- city-neighborhood-reference:end -->\n?",
                  "", page, flags=re.S)
    marker = '<footer class="site-footer">'
    if page.count(marker) != 1:
        raise ValueError(f"Expected a single site footer in {path}")
    if STYLE not in page:
        page = page.replace("</head>", STYLE + "</head>", 1)
    path.write_text(page.replace(marker, '<!-- city-neighborhood-reference:start -->'
                                 + markup + '<!-- city-neighborhood-reference:end -->\n' + marker, 1))


def reference(item, by_slug, city):
    name = escape(item["name"])
    bounds = " ".join(map(str, item["view"]))
    population = (
        f'<div><dt>Estimated population, 2018–2022 ACS</dt><dd>{item["population"]:,}</dd></div>'
        if item["population"] is not None else ""
    )
    neighbors = ", ".join(link(route(k), by_slug[k]["name"]) for k in item["adjacent"])
    sources = [link(BOUNDARIES, "City GIS boundary data"), link(WARDS, "City council districts and wards")]
    if item["population"] is not None:
        sources.append(link(ACS, "UCSUR neighborhood population estimates"))
    if item["snapshot"]:
        sources.append(link(f'https://engage.pittsburghpa.gov/download_file/{item["snapshot"]}/1852',
                            f'City of Pittsburgh snapshot for {item["name"]} (PDF)'))
    else:
        sources.append(link(SNAPSHOTS, "City neighborhood snapshots"))
    related = REGIONAL_GUIDES.get(item["name"])
    reporting = f'<p>Read the Wire’s broader {link(*related)} coverage.</p>' if related else ""
    boundary = f'<p>City neighborhoods sharing a boundary on this map include {neighbors}.</p>'
    return f'''<section class="city-reference" aria-labelledby="boundary-details">
<h2 id="boundary-details">{name} map and boundaries</h2>
<figure><svg viewBox="{bounds}" role="img" aria-label="Map highlighting {name}" xmlns="http://www.w3.org/2000/svg">
<path d="{city}" fill="#e5ddd0" fill-rule="evenodd" aria-hidden="true"/>
<path d="{item["path"]}" fill="#a51a30" fill-opacity=".78" fill-rule="evenodd" stroke="#6f0d1c" stroke-width="1.4" aria-hidden="true"/>
</svg><figcaption>{name} is highlighted. Boundaries are simplified for display.</figcaption></figure>
<dl><div><dt>Mapped area</dt><dd>About {item["area"]:,} acres</dd></div>{population}</dl>
{boundary}{reporting}
<h2>Sources and address lookup</h2>
<p>Use the city’s ward tools to look up an address or elected district. Neighborhood and ward boundaries are drawn for different purposes.</p>
<ul>{''.join(f'<li>{source}</li>' for source in sources)}</ul>
<p>{link(INDEX + "#all-city-neighborhoods", "See all 90 Pittsburgh neighborhoods")}</p></section>'''


def publish():
    data = json.loads((ROOT / "data/city-neighborhood-boundaries.json").read_text())
    items = data["neighborhoods"]
    by_slug = {item["slug"]: item for item in items}
    if len(items) != 90 or len(by_slug) != len(items):
        raise ValueError("Expected 90 distinct city neighborhoods")
    added = 0
    for item in items:
        url = route(item["slug"])
        path = ROOT / url.strip("/") / "index.html"
        content = reference(item, by_slug, data["city"])
        if item["existing"]:
            inject(path, content)
            continue
        title = item["name"] + ", Pittsburgh"
        description = f"Find {item['name']} on Pittsburgh’s neighborhood map, see bordering areas, and check official boundary and ward sources."
        body = f'''<div class="breadcrumb">{link("/", "Home")}<span>/</span>{link(INDEX, "Neighborhoods")}</div>
<header class="page-head"><h1 class="page-title">{escape(title)}</h1><p class="page-deck">{escape(description)}</p></header><main>{content}</main>'''
        page = page_shell(escape(title + " Neighborhood Map | The Pittsburgh Wire"), escape(description),
                          SITE + url, body)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page.replace("</head>", STYLE + "</head>", 1))
        added += 1

    navigation = '<section class="city-reference" id="all-city-neighborhoods"><h2>All 90 Pittsburgh city neighborhoods</h2>'
    navigation += '<p>Browse the city’s mapped neighborhood boundaries. Each entry links to a map and the official sources for checking addresses.</p>'
    navigation += '<ul class="city-neighborhood-list">' + "".join(
        f'<li>{link(route(item["slug"]), item["name"])}</li>' for item in items) + "</ul></section>"
    directory = ROOT / "neighborhoods/index.html"
    inject(directory, navigation)
    index = directory.read_text()
    if 'href="#all-city-neighborhoods"' not in index:
        index = re.sub(r"(</h1>)", r'\1<p><a href="#all-city-neighborhoods">Browse all 90 city neighborhoods</a></p>', index, count=1)
        directory.write_text(index)

    sitemap = ROOT / "sitemap.xml"
    xml = sitemap.read_text()
    entries = []
    for item in items:
        loc = f'<loc>{SITE}{route(item["slug"])}</loc>'
        if loc not in xml:
            entries.append(f"  <url>{loc}</url>\n")
    sitemap.write_text(xml.replace("</urlset>", "".join(entries) + "</urlset>", 1))
    return added


if __name__ == "__main__":
    print(f"Published {publish()} new neighborhood pages and a complete 90-neighborhood index.")
