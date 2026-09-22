"""Small directory profiles checked against each organization's own site."""

from html import escape
from pathlib import Path

from directory_index import VERIFIED_CATEGORY


DATA = {
    "baum-boulevard-automotive": {
        "name": "Baum Boulevard Automotive", "address": "4741 Baum Boulevard, Pittsburgh, PA 15213",
        "summary": "Pittsburgh auto repair shop on Baum Boulevard offering maintenance and diagnostic services.",
        "site": "https://www.baumblvdauto.com/", "source": "https://www.baumblvdauto.com/about",
    },
    "carnegie-robotics": {
        "name": "Carnegie Robotics", "address": "4501 Hatfield Street, Pittsburgh, PA 15201",
        "summary": "Pittsburgh robotics company developing sensors, autonomous systems, and manufacturing services.",
        "site": "https://www.carnegierobotics.com/", "source": "https://www.carnegierobotics.com/about",
    },
    "chatham-university": {
        "name": "Chatham University", "address": "107 Woodland Road, Pittsburgh, PA 15232",
        "summary": "University with a Shadyside campus and additional Pittsburgh area locations.",
        "site": "https://www.chatham.edu/", "source": "https://www.chatham.edu/about-us/",
    },
    "dollar-bank": {
        "name": "Dollar Bank", "address": "20 Stanwix Street, Pittsburgh, PA 15222",
        "summary": "Pittsburgh based bank whose headquarters is at 20 Stanwix Street. This address is an office, not a retail branch.",
        "site": "https://dollar.bank/", "source": "https://locations.dollar.bank/headquarters/pittsburgh-headquarters",
    },
    "gecko-robotics": {
        "name": "Gecko Robotics", "address": "100 S Commons, Suite 145, Pittsburgh, PA 15212",
        "summary": "Pittsburgh headquartered robotics and software company focused on inspection and maintenance data for industrial infrastructure.",
        "site": "https://www.geckorobotics.com/", "source": "https://www.geckorobotics.com/contact",
    },
    "pamelas-diner": {
        "name": "P&G Pamela's Diner", "address": "60 21st Street, Pittsburgh, PA 15222 (Strip District location)",
        "summary": "Pittsburgh diner with locations in the Strip District, Mt. Lebanon, Shadyside, and Oakland. Check the official site for each location's current hours.",
        "site": "https://pamelasdiner.com/", "source": "https://pamelasdiner.com/",
    },
    "pj-dick": {
        "name": "PJ Dick", "address": "30 Isabella Street, Suite 500, Pittsburgh, PA 15212",
        "summary": "Family owned construction firm providing general contracting, construction management, and related services.",
        "site": "https://pjdick.com/", "source": "https://pjdick.com/about",
    },
    "pnc-financial-services": {
        "name": "PNC Financial Services", "address": "300 Fifth Avenue, Pittsburgh, PA 15222",
        "summary": "Financial services group headquartered at the Tower at PNC Plaza in Downtown Pittsburgh.",
        "site": "https://www.pnc.com/", "source": "https://investor.pnc.com/company-information/faqs",
    },
    "pittsburgh-cultural-trust": {
        "name": "Pittsburgh Cultural Trust", "address": "Pittsburgh Cultural District, Downtown Pittsburgh",
        "summary": "Nonprofit arts organization presenting performing and visual arts, festivals, and arts education in Downtown Pittsburgh's Cultural District.",
        "site": "https://trustarts.org/", "source": "https://trustarts.org/pct_home/about",
    },
    "primanti-brothers": {
        "name": "Primanti Bros.", "address": "46 18th Street, Pittsburgh, PA 15222 (Strip District location)",
        "summary": "Pittsburgh restaurant group with locations including the Strip District, Oakland, Market Square, and South Side. Check its location directory for current details.",
        "site": "https://primantibros.com/", "source": "https://restaurants.primantibros.com/locations/pa/pittsburgh",
    },
    "walnut-capital": {
        "name": "Walnut Capital", "address": "5500 Walnut Street, Suite 300, Pittsburgh, PA 15232",
        "summary": "Pittsburgh real estate company providing property management and leasing for residential and commercial properties.",
        "site": "https://www.walnutcapital.com/", "source": "https://www.walnutcapital.com/contact",
    },
}


def write(repo, page_shell):
    base = Path(repo) / "directory"
    for slug, item in DATA.items():
        if slug not in VERIFIED_CATEGORY:
            raise ValueError(f"Missing category for {slug}")
        name, summary, address = (escape(item[key], quote=True) for key in ("name", "summary", "address"))
        source = escape(item["source"], quote=True)
        site = escape(item["site"], quote=True)
        body = f'''<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/directory/">Directory</a><span>/</span><a href="/directory/{VERIFIED_CATEGORY[slug]}/">{escape(VERIFIED_CATEGORY[slug].replace('-', ' ').title())}</a><span>/</span><span>{name}</span></div>
  <div class="page-head"><span class="page-eyebrow">Pittsburgh business directory</span><h1 class="page-title">{name}</h1><p class="page-deck">{summary}</p></div>
  <main class="archive"><h2 class="month-head">What we checked</h2><p>{summary}</p><p style="margin-top:18px"><strong>Address:</strong> {address}</p><p style="margin-top:18px"><a href="{site}" rel="noopener noreferrer" style="text-decoration:underline">Visit the official site</a> · <a href="{source}" rel="noopener noreferrer" style="text-decoration:underline">Source for this profile</a></p><p style="margin-top:18px">Details checked September 22, 2026. <a href="/contact" style="text-decoration:underline">Send a correction</a> if information changes.</p></main>'''
        url = f"https://www.thepittsburghwire.com/directory/{slug}/"
        markup = page_shell(f"{name} | Pittsburgh Business Directory | The Pittsburgh Wire", summary, url, body, active_nav="/directory")
        (base / slug / "index.html").write_text(markup, encoding="utf-8")
