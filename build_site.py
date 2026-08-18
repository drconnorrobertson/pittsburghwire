#!/usr/bin/env python3
"""
build_site.py -- The Pittsburgh Wire site builder

Scans /news/ for published articles and regenerates every derived page:

    index.html            homepage dynamic sections (ticker, lead, 3-col, belt,
                          people, "More from The Wire")
    news/index.html       the full archive -- text-only story cards
    news/<category>/      one index per section (business, real-estate,
                          development, people, neighborhoods)
    best/index.html       "Best of Pittsburgh" hub
    sitemap.xml           every page on the site

The site is text-only by design: no hero photos, no card thumbnails, no stock
imagery anywhere. Do not reintroduce <img> tags into generated output.

Usage:
    python3 build_site.py                 # run from repo root
    python3 build_site.py /path/to/repo
"""

import re
import os
import sys
import html as html_mod
from collections import OrderedDict

SITE = "https://www.thepittsburghwire.com"

MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}
MONTH_NUMS = {v: k for k, v in MONTH_NAMES.items()}

# canonical sections -> url slug
CATEGORIES = OrderedDict([
    ("Business", "business"),
    ("Real Estate", "real-estate"),
    ("Development", "development"),
    ("People", "people"),
    ("Neighborhoods", "neighborhoods"),
])
CATEGORY_BLURB = {
    "Business": "Companies, funding rounds, expansions, and the deals moving "
                "Pittsburgh's economy forward.",
    "Real Estate": "Transactions, market shifts, and the buildings changing "
                   "hands across the region.",
    "Development": "Construction, infrastructure, and the projects reshaping "
                   "Pittsburgh's skyline and streets.",
    "People": "The founders, builders, chefs, and civic leaders behind "
              "Pittsburgh's momentum.",
    "Neighborhoods": "Block-by-block coverage of the districts that make up "
                     "the city.",
}

# normalise the labels that appear in the wild
CATEGORY_ALIASES = {
    "development &bull; people": "Development",
    "development • people": "Development",
    "people &amp; community": "People",
    "people & community": "People",
    "community": "Neighborhoods",
    "dining": "Business",
    "technology": "Business",
    "healthcare": "Business",
    "hospitality": "Business",
    "arts": "Neighborhoods",
    "culture": "Neighborhoods",
}


# ---------------------------------------------------------------------------
# SHARED CHROME  (identical markup on every generated page)
# ---------------------------------------------------------------------------
def topbar():
    return """  <div class="topbar">
    <span class="topbar-date" data-today>Pittsburgh, Pennsylvania</span>
    <div class="topbar-links">
      <a href="/news/">News</a>
      <a href="/neighborhoods">Neighborhoods</a>
      <a href="/best/">Best Of</a>
      <a href="/weekly">Weekly</a>
      <a href="/about">About</a>
      <a href="/directory" class="topbar-sister">&#9670; Business Directory</a>
    </div>
  </div>"""


MASTHEAD = """  <header class="masthead">
    <p class="masthead-tagline">Pittsburgh Business &bull; Real Estate &bull; Development &bull; People</p>
    <a href="/"><div class="masthead-title">The Pittsburgh Wire</div></a>
    <p class="masthead-tagline">Good News, Only. Always Forward.</p>
  </header>"""

NAV_LINKS = [
    ("/", "Home"),
    ("/news/", "News"),
    ("/news/business/", "Business"),
    ("/news/real-estate/", "Real Estate"),
    ("/news/development/", "Development"),
    ("/news/people/", "People"),
    ("/neighborhoods", "Neighborhoods"),
    ("/directory", "Directory"),
    ("/best/", "Best Of"),
    ("/about", "About"),
]


def nav(active=None):
    out = ['  <nav class="nav">', '    <div class="nav-inner">']
    for href, label in NAV_LINKS:
        cls = ' class="active"' if href == active else ''
        out.append(f'      <a href="{href}"{cls}>{label}</a>')
    out += ['    </div>', '  </nav>']
    return "\n".join(out)


FOOTER = """  <footer class="site-footer">
    <div class="site-footer-inner">
      <div class="site-footer-masthead"><a href="/">The Pittsburgh Wire</a></div>
      <p class="site-footer-tagline">Good News, Only. Always Forward.</p>
      <div class="site-footer-cols">
        <div class="site-footer-col">
          <p class="site-footer-col-head">About</p>
          <p>An independent digital publication covering Pittsburgh business, real estate, economic development, and the people building the city. We publish good news only.</p>
        </div>
        <div class="site-footer-col">
          <p class="site-footer-col-head">Coverage</p>
          <ul>
            <li><a href="/news/">All Stories</a></li>
            <li><a href="/news/business/">Business</a></li>
            <li><a href="/news/real-estate/">Real Estate</a></li>
            <li><a href="/news/development/">Development</a></li>
            <li><a href="/news/people/">People</a></li>
            <li><a href="/news/neighborhoods/">Neighborhoods</a></li>
          </ul>
        </div>
        <div class="site-footer-col">
          <p class="site-footer-col-head">Explore</p>
          <ul>
            <li><a href="/directory">Business Directory</a></li>
            <li><a href="/best/">Best of Pittsburgh</a></li>
            <li><a href="/neighborhoods">Neighborhoods</a></li>
            <li><a href="/weekly">The Weekly</a></li>
            <li><a href="/author">Our Team</a></li>
          </ul>
        </div>
        <div class="site-footer-col">
          <p class="site-footer-col-head">Contact</p>
          <ul>
            <li><a href="/contact">Contact Us</a></li>
            <li><a href="mailto:tips@pittsburghwire.com">Submit a Tip</a></li>
            <li><a href="/about">About The Wire</a></li>
            <li><a href="/privacy">Privacy Policy</a></li>
          </ul>
        </div>
      </div>
      <p class="site-footer-copy">&copy; 2026 The Pittsburgh Wire. All rights reserved. Pittsburgh, Pennsylvania.</p>
    </div>
  </footer>"""


# ---------------------------------------------------------------------------
# LISTING PAGE STYLESHEET  (shared by /news/, category pages, /best/)
# ---------------------------------------------------------------------------
LISTING_CSS = """    :root{--ink:#0f0e0c;--paper:#f5f0e8;--cream:#ede8dc;--rule:#c8bfad;--accent:#b5001f;--smoke:#6b6355;--light-smoke:#a09585}
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    html{scroll-behavior:smooth}
    body{background:var(--paper);color:var(--ink);font-family:'Source Serif 4',Georgia,serif;font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
    a{color:inherit;text-decoration:none}
    .topbar{background:var(--ink);color:var(--paper);padding:7px 28px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;font-family:'Barlow Condensed',sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase}
    .topbar-date{color:var(--light-smoke)}
    .topbar-links{display:flex;gap:18px;flex-wrap:wrap}
    .topbar-links a{color:#aaa;transition:color .15s}
    .topbar-links a:hover{color:var(--paper)}
    .topbar-sister{color:#d8a53c;border:1px solid #8a6a00;padding:2px 10px}
    .masthead{border-bottom:4px double var(--ink);padding:24px 28px 16px;text-align:center}
    .masthead-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(32px,6vw,72px);font-weight:900;line-height:.92;letter-spacing:-2px;color:var(--ink);margin:12px 0 8px}
    .masthead-tagline{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:var(--smoke)}
    .nav{background:var(--ink);position:relative}
    .nav-inner{max-width:1400px;margin:0 auto;display:flex;justify-content:center;flex-wrap:wrap}
    .nav a{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:var(--paper);padding:11px 18px;display:block;border-right:1px solid #2a2a2a;transition:background .15s}
    .nav a:first-child{border-left:1px solid #2a2a2a}
    .nav a:hover{background:var(--accent)}
    .nav a.active{background:var(--accent)}
    .breadcrumb{max-width:1200px;margin:0 auto;padding:16px 28px 0;font-family:'Barlow Condensed',sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--light-smoke);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
    .breadcrumb a:hover{color:var(--accent)}
    .page-head{max-width:1200px;margin:0 auto;padding:24px 28px 28px;border-bottom:4px double var(--rule)}
    .page-eyebrow{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:var(--accent);display:inline-block;border-bottom:2px solid var(--accent);padding-bottom:4px;margin-bottom:16px}
    .page-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(30px,5vw,54px);font-weight:900;line-height:1.05;letter-spacing:-1px;margin-bottom:14px}
    .page-deck{font-size:18px;font-style:italic;color:var(--smoke);max-width:680px;line-height:1.6}
    .page-count{font-family:'Barlow Condensed',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--light-smoke);margin-top:16px}
    .cat-bar{max-width:1200px;margin:0 auto;padding:20px 28px;display:flex;gap:10px;flex-wrap:wrap;border-bottom:1px solid var(--rule)}
    .cat-chip{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:7px 16px;border:1px solid var(--rule);color:var(--smoke);background:var(--cream);transition:background .15s,color .15s,border-color .15s}
    .cat-chip:hover{background:var(--ink);color:var(--paper);border-color:var(--ink)}
    .cat-chip.active{background:var(--accent);border-color:var(--accent);color:#fff}
    .archive{max-width:1200px;margin:0 auto;padding:40px 28px 64px}
    .month-head{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:var(--ink);display:flex;align-items:center;gap:14px;margin:44px 0 22px}
    .month-head:first-child{margin-top:0}
    .month-head::after{content:'';flex:1;height:1px;background:var(--rule)}
    .card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));gap:1px;background:var(--rule);border:1px solid var(--rule)}
    .story-card{background:var(--paper);padding:26px 28px 24px;display:flex;flex-direction:column;gap:10px;transition:background .15s}
    .story-card:hover{background:var(--cream)}
    .card-label{font-family:'Barlow Condensed',sans-serif;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--accent)}
    .card-headline{font-family:'Playfair Display',Georgia,serif;font-size:21px;font-weight:700;line-height:1.25;letter-spacing:-.2px}
    .card-headline a:hover{color:var(--accent)}
    .card-date{font-family:'Barlow Condensed',sans-serif;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--light-smoke)}
    .card-excerpt{font-size:15px;line-height:1.65;color:var(--smoke);flex:1}
    .card-more{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--accent);margin-top:4px}
    .card-more:hover{text-decoration:underline}
    .empty-note{padding:48px 0;font-style:italic;color:var(--smoke)}
    .footer{background:var(--ink);color:var(--paper);padding:48px 28px 28px}
    .footer-inner{max-width:1400px;margin:0 auto}
    .footer-masthead{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,5vw,42px);font-weight:900;letter-spacing:-1px;margin-bottom:6px}
    .footer-tagline{font-family:'Barlow Condensed',sans-serif;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#666;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid #222}
    .footer-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:32px;margin-bottom:32px}
    .footer-col-head{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:var(--paper);margin-bottom:12px}
    .footer-col p{font-size:14px;line-height:1.7;color:#8a8a8a}
    .footer-links-list{list-style:none}
    .footer-links-list li{margin-bottom:7px}
    .footer-links-list a{font-size:14px;color:#8a8a8a;transition:color .15s}
    .footer-links-list a:hover{color:var(--paper)}
    .footer-copy{font-family:'Barlow Condensed',sans-serif;font-size:11px;letter-spacing:1px;color:#444;padding-top:20px;border-top:1px solid #222}
    @media(max-width:768px){
      .topbar{padding:7px 16px}
      .topbar-links{display:none}
      .masthead{padding:16px 16px 12px}
      .breadcrumb,.page-head,.cat-bar,.archive{padding-left:16px;padding-right:16px}
      .archive{padding-top:28px}
      .story-card{padding:22px 18px}
      .footer{padding:36px 16px 24px}
    }"""


def page_shell(title, description, canonical, body, active_nav=None):
    """Wrap generated body markup in the shared document shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{canonical}" />
  <meta name="twitter:card" content="summary" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet" />
  <style>
{LISTING_CSS}
  </style>
  <link rel="stylesheet" href="/css/site.css" />
  <link rel="stylesheet" href="/css/mobile.css" />
  <script src="/js/mobile-nav.js" defer></script>
  <script src="/js/site.js" defer></script>
</head>
<body>
{topbar()}
{MASTHEAD}
{nav(active_nav)}
{body}
{FOOTER}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# ARTICLE SCANNER
# ---------------------------------------------------------------------------
def clean(text):
    """Collapse whitespace and unescape stray entities for re-escaping."""
    return re.sub(r'\s+', ' ', html_mod.unescape(text or '')).strip()


def normalize_category(raw):
    raw = clean(raw)
    key = raw.lower()
    if key in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[key]
    for cat in CATEGORIES:
        if key == cat.lower():
            return cat
    return "Business"


def scan_articles(repo):
    news_dir = os.path.join(repo, "news")
    reserved = set(CATEGORIES.values())      # generated category indexes
    articles = []
    for slug in sorted(os.listdir(news_dir)):
        if slug in reserved or slug.startswith("."):
            continue
        fpath = os.path.join(news_dir, slug, "index.html")
        if not os.path.isfile(fpath):
            continue
        c = open(fpath, encoding="utf-8", errors="ignore").read()

        # date
        m = (re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', c)
             or re.search(r'article:published_time"\s+content="(\d{4}-\d{2}-\d{2})', c)
             or re.search(r'content="(\d{4}-\d{2}-\d{2})', c))
        if m:
            date = m.group(1)
        else:
            m2 = re.search(r'(January|February|March|April|May|June|July|August|'
                           r'September|October|November|December)\s+(\d+),\s+(\d{4})', c)
            if not m2:
                print("  ! no date, skipping:", slug)
                continue
            date = f"{m2.group(3)}-{MONTH_NUMS[m2.group(1)]}-{int(m2.group(2)):02d}"

        tm = re.search(r'<title>([^|<]+)', c)
        title = clean(tm.group(1)) if tm else slug.replace("-", " ").title()

        dm = re.search(r'name="description"\s+content="([^"]*)"', c)
        desc = clean(dm.group(1)) if dm else ""

        cm = (re.search(r'class="article-section-label"[^>]*>([^<]+)<', c)
              or re.search(r'class="article-section"[^>]*>([^<]+)<', c)
              or re.search(r'class="story-label"[^>]*>([^<]+)<', c))
        cat = normalize_category(cm.group(1) if cm else "")

        bm = (re.search(r'class="article-byline"[^>]*>\s*By\s*(?:<a[^>]*>)?([^<]+)', c)
              or re.search(r'By\s+<span>([^<]+)', c))
        byline = clean(bm.group(1)) if bm else "The Pittsburgh Wire Staff"

        y, mo, d = date.split("-")
        articles.append({
            "slug": slug, "date": date, "title": title, "desc": desc,
            "cat": cat, "byline": byline,
            "display_date": f"{MONTH_NAMES[mo]} {int(d)}, {y}",
            "month_key": f"{y}-{mo}",
            "month_label": f"{MONTH_NAMES[mo]} {y}",
        })
    articles.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    return articles


# ---------------------------------------------------------------------------
# CARD / LISTING BUILDERS
# ---------------------------------------------------------------------------
def esc(s):
    return html_mod.escape(s or "", quote=True)


def excerpt(a, limit=165):
    text = a["desc"]
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "&hellip;"
        return text
    return esc(text)


def story_card(a):
    return f"""          <article class="story-card">
            <span class="card-label">{esc(a["cat"])}</span>
            <h2 class="card-headline"><a href="/news/{a["slug"]}">{esc(a["title"])}</a></h2>
            <p class="card-date">{a["display_date"]}</p>
            <p class="card-excerpt">{excerpt(a)}</p>
            <a class="card-more" href="/news/{a["slug"]}">Read More &rarr;</a>
          </article>"""


def cat_bar(active_slug=None):
    chips = ['      <a class="cat-chip%s" href="/news/">All Stories</a>'
             % ('' if active_slug else ' active')]
    for label, slug in CATEGORIES.items():
        cls = ' active' if slug == active_slug else ''
        chips.append(f'      <a class="cat-chip{cls}" href="/news/{slug}/">{label}</a>')
    return '    <div class="cat-bar">\n' + "\n".join(chips) + '\n    </div>'


def grouped_archive(articles):
    """Cards grouped under month headings, newest month first."""
    if not articles:
        return '      <p class="empty-note">No stories filed yet. Check back soon.</p>'
    out = []
    current = None
    for a in articles:
        if a["month_key"] != current:
            if current is not None:
                out.append("        </div>")
            current = a["month_key"]
            out.append(f'        <h2 class="month-head">{a["month_label"]}</h2>')
            out.append('        <div class="card-grid">')
        out.append(story_card(a))
    out.append("        </div>")
    return "\n".join(out)


def flat_archive(articles):
    if not articles:
        return '      <p class="empty-note">No stories filed yet. Check back soon.</p>'
    return ('        <div class="card-grid">\n'
            + "\n".join(story_card(a) for a in articles)
            + "\n        </div>")


# ---------------------------------------------------------------------------
# PAGE BUILDERS
# ---------------------------------------------------------------------------
def build_news_index(repo, articles):
    body = f"""  <div class="breadcrumb">
    <a href="/">Home</a>
    <span>/</span>
    <span>News</span>
  </div>

  <div class="page-head">
    <span class="page-eyebrow">The Archive</span>
    <h1 class="page-title">All Stories</h1>
    <p class="page-deck">Every story The Pittsburgh Wire has published &mdash; business, real estate, development, people, and neighborhoods. Newest first.</p>
    <p class="page-count">{len(articles)} stories &bull; updated {articles[0]["display_date"] if articles else ""}</p>
  </div>

{cat_bar(None)}

  <main class="archive">
{grouped_archive(articles)}
  </main>"""
    out = page_shell(
        "All Stories | The Pittsburgh Wire",
        "Browse every story from The Pittsburgh Wire: Pittsburgh business, real estate, "
        "development, people, and neighborhood news, newest first.",
        f"{SITE}/news/", body, active_nav="/news/")
    path = os.path.join(repo, "news", "index.html")
    open(path, "w", encoding="utf-8").write(out)
    return path


def build_category_pages(repo, articles):
    made = []
    for label, slug in CATEGORIES.items():
        subset = [a for a in articles if a["cat"] == label]
        body = f"""  <div class="breadcrumb">
    <a href="/">Home</a>
    <span>/</span>
    <a href="/news/">News</a>
    <span>/</span>
    <span>{label}</span>
  </div>

  <div class="page-head">
    <span class="page-eyebrow">Section</span>
    <h1 class="page-title">{label}</h1>
    <p class="page-deck">{CATEGORY_BLURB[label]}</p>
    <p class="page-count">{len(subset)} {"story" if len(subset) == 1 else "stories"}</p>
  </div>

{cat_bar(slug)}

  <main class="archive">
{flat_archive(subset)}
  </main>"""
        out = page_shell(
            f"{label} News | The Pittsburgh Wire",
            f"{CATEGORY_BLURB[label]} Pittsburgh {label.lower()} coverage from The Pittsburgh Wire.",
            f"{SITE}/news/{slug}/", body,
            active_nav=f"/news/{slug}/" if f"/news/{slug}/" in dict(NAV_LINKS) else "/news/")
        d = os.path.join(repo, "news", slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
        made.append((label, len(subset)))
    return made


def scan_best(repo):
    """Read every /best/<slug>/ page and pull its headline."""
    best_dir = os.path.join(repo, "best")
    items = []
    for slug in sorted(os.listdir(best_dir)):
        p = os.path.join(best_dir, slug, "index.html")
        if not os.path.isfile(p):
            continue
        c = open(p, encoding="utf-8", errors="ignore").read()
        m = re.search(r'class="hero-headline"[^>]*>([^<]+)<', c) or re.search(r'<title>([^|<]+)', c)
        title = clean(m.group(1)) if m else slug.replace("-", " ").title()
        dm = re.search(r'name="description"\s+content="([^"]*)"', c)
        items.append({"slug": slug, "title": title, "desc": clean(dm.group(1)) if dm else ""})
    return items


def build_best_index(repo):
    items = scan_best(repo)
    # group by category (the part before " in ")
    groups = OrderedDict()
    for it in items:
        m = re.match(r'(.+?)-in-(.+)$', it["slug"])
        cat = (m.group(1) if m else it["slug"]).replace("-", " ").title()
        groups.setdefault(cat, []).append(it)

    sections = []
    for cat in sorted(groups):
        cards = []
        for it in sorted(groups[cat], key=lambda x: x["title"]):
            place = it["slug"].split("-in-", 1)[-1].replace("-", " ").title()
            cards.append(f"""          <article class="story-card">
            <span class="card-label">{esc(cat)}</span>
            <h2 class="card-headline"><a href="/best/{it["slug"]}">{esc(it["title"])}</a></h2>
            <p class="card-date">{esc(place)}</p>
            <a class="card-more" href="/best/{it["slug"]}">View The List &rarr;</a>
          </article>""")
        sections.append(f'        <h2 class="month-head">{esc(cat)}</h2>\n'
                        '        <div class="card-grid">\n'
                        + "\n".join(cards) + "\n        </div>")

    body = f"""  <div class="breadcrumb">
    <a href="/">Home</a>
    <span>/</span>
    <span>Best Of</span>
  </div>

  <div class="page-head">
    <span class="page-eyebrow">Best Of Pittsburgh</span>
    <h1 class="page-title">The Best of Pittsburgh</h1>
    <p class="page-deck">Neighborhood-by-neighborhood guides to the best businesses and services across the Pittsburgh region, researched and maintained by The Pittsburgh Wire.</p>
    <p class="page-count">{len(items)} guides</p>
  </div>

  <main class="archive">
{chr(10).join(sections)}
  </main>"""
    out = page_shell(
        "Best of Pittsburgh | The Pittsburgh Wire",
        "Neighborhood guides to the best businesses and services in Pittsburgh "
        "— accountants, contractors, restaurants, photographers, and more.",
        f"{SITE}/best/", body, active_nav="/best/")
    open(os.path.join(repo, "best", "index.html"), "w", encoding="utf-8").write(out)
    return len(items)


# ---------------------------------------------------------------------------
# HOMEPAGE SECTIONS  (text only)
# ---------------------------------------------------------------------------
def gen_ticker(articles):
    top = articles[:6]
    spans = "".join(f'      <span>{esc(a["title"])}</span>\n' for a in top + top[:2])
    return spans


def gen_lead(articles):
    a0, a1, a2 = articles[0], articles[1], articles[2]
    side = ""
    for a in (a1, a2):
        side += f"""          <div class="sidebar-story">
            <span class="story-label">{esc(a["cat"])}</span>
            <p class="sidebar-headline"><a href="/news/{a["slug"]}">{esc(a["title"])}</a></p>
            <p class="sidebar-deck">{excerpt(a, 150)}</p>
          </div>
"""
    return f"""
        <div class="lead-main">
          <span class="story-label">{esc(a0["cat"])}</span>
          <h2 class="lead-headline">
            <a href="/news/{a0["slug"]}">{esc(a0["title"])}</a>
          </h2>
          <p class="lead-deck">{esc(a0["desc"])}</p>
          <p class="byline">By {esc(a0["byline"])} &bull; {a0["display_date"]}</p>
        </div>
        <div class="lead-sidebar">
{side}        </div>
      """


def gen_threecol(articles):
    out = ""
    for a in articles[3:6]:
        out += f"""
        <div class="col-story">
          <span class="story-label">{esc(a["cat"])}</span>
          <p class="col-headline"><a href="/news/{a["slug"]}">{esc(a["title"])}</a></p>
          <p class="col-deck">{excerpt(a, 175)}</p>
          <p class="byline">{a["display_date"]}</p>
        </div>"""
    return out + "\n      "


def gen_belt(articles):
    """Development & Real Estate belt -- prefer stories actually in those sections."""
    picks = [a for a in articles if a["cat"] in ("Development", "Real Estate")][:4]
    if len(picks) < 4:
        picks += [a for a in articles[6:] if a not in picks][:4 - len(picks)]
    out = ""
    for a in picks:
        out += f"""
          <div class="belt-item">
            <div class="belt-cat">{esc(a["cat"])}</div>
            <p class="belt-headline"><a href="/news/{a["slug"]}" style="color:inherit">{esc(a["title"])}</a></p>
            <p class="belt-byline">{a["display_date"]}</p>
          </div>"""
    return out + "\n        "


def gen_people(articles):
    """People of Pittsburgh -- the three most recent People stories.

    No initials medallion: the old generator derived one from the first two
    words of the headline, which produced meaningless monograms like "MG" for
    "Michelin Guide". These are stories, so they are labelled like stories.
    """
    picks = [a for a in articles if a["cat"] == "People"][:3]
    if len(picks) < 3:
        picks += [a for a in articles if a not in picks][:3 - len(picks)]
    out = ""
    for a in picks:
        out += f"""
        <div class="person-card">
          <p class="person-title">{esc(a["cat"])} &bull; {a["display_date"]}</p>
          <p class="person-name"><a href="/news/{a["slug"]}">{esc(a["title"])}</a></p>
          <p class="person-desc">{excerpt(a, 190)}</p>
        </div>"""
    return out + "\n      "


def gen_more_cards(articles):
    """More from The Wire -- text-only cards, no thumbnails."""
    out = ""
    for a in articles[10:40]:
        out += f"""          <div class="more-card">
            <span class="more-card-label">{esc(a["cat"])}</span>
            <p class="more-card-headline"><a href="/news/{a["slug"]}">{esc(a["title"])}</a></p>
            <p class="more-card-date">By {esc(a["byline"])} &bull; {a["display_date"]}</p>
          </div>
"""
    return out


def replace_inner(html, open_tag_re, new_inner, name):
    """Replace the inner HTML of the first <div> whose opening tag matches.

    Uses depth counting so it is immune to how many nested divs the section
    contains -- unlike a non-greedy regex, which silently eats the wrong
    closing tag when the markup shifts.
    """
    m = re.search(open_tag_re, html)
    if not m:
        print("  ! homepage section not matched:", name)
        return html
    i = m.end()
    depth = 1
    tag = re.compile(r'<\s*(/?)div\b', re.I)
    while depth > 0:
        t = tag.search(html, i)
        if not t:
            print("  ! unbalanced markup in section:", name)
            return html
        if t.group(1):
            depth -= 1
            if depth == 0:
                return html[:m.end()] + new_inner + html[t.start():]
        else:
            depth += 1
        i = t.end()
    return html


def update_homepage(repo, articles):
    index_path = os.path.join(repo, "index.html")
    html = open(index_path, encoding="utf-8").read()

    sections = [
        (r'<div class="ticker-inner">', "\n" + gen_ticker(articles) + "    ", "ticker"),
        (r'<div class="lead-grid[^"]*">', gen_lead(articles) + "\n      ", "lead"),
        (r'<div class="three-col[^"]*">', gen_threecol(articles), "three-col"),
        (r'<div class="belt-grid">', gen_belt(articles), "belt"),
        (r'<div class="people-grid[^"]*">', gen_people(articles), "people"),
        (r'<div class="more-grid">', "\n" + gen_more_cards(articles) + "        ", "more"),
    ]
    for pat, content, name in sections:
        html = replace_inner(html, pat, content, name)

    open(index_path, "w", encoding="utf-8").write(html)


# ---------------------------------------------------------------------------
# SITEMAP
# ---------------------------------------------------------------------------
def build_sitemap(repo, articles):
    urls = []

    def add(loc, pri, freq="weekly", lastmod=None):
        entry = f"  <url>\n    <loc>{loc}</loc>\n"
        if lastmod:
            entry += f"    <lastmod>{lastmod}</lastmod>\n"
        entry += f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>"
        urls.append(entry)

    newest = articles[0]["date"] if articles else None
    add(f"{SITE}/", "1.0", "daily", newest)
    add(f"{SITE}/news/", "0.9", "daily", newest)
    for slug in CATEGORIES.values():
        add(f"{SITE}/news/{slug}/", "0.8", "daily", newest)
    add(f"{SITE}/directory", "0.8", "weekly")
    add(f"{SITE}/neighborhoods", "0.8", "weekly")
    add(f"{SITE}/best/", "0.8", "weekly")
    add(f"{SITE}/weekly", "0.7", "weekly")
    add(f"{SITE}/about", "0.6", "monthly")
    add(f"{SITE}/author", "0.5", "monthly")
    add(f"{SITE}/contact", "0.5", "monthly")
    add(f"{SITE}/privacy", "0.3", "yearly")

    for a in articles:
        add(f"{SITE}/news/{a['slug']}", "0.9", "monthly", a["date"])

    for section, pri in (("best", "0.7"), ("directory", "0.6"), ("neighborhoods", "0.7")):
        d = os.path.join(repo, section)
        for slug in sorted(os.listdir(d)):
            if os.path.isfile(os.path.join(d, slug, "index.html")):
                add(f"{SITE}/{section}/{slug}", pri, "monthly")

    for slug in sorted(os.listdir(os.path.join(repo, "authors"))):
        if os.path.isfile(os.path.join(repo, "authors", slug, "index.html")):
            add(f"{SITE}/authors/{slug}", "0.5", "monthly")

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(repo, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    return len(urls)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main(repo):
    articles = scan_articles(repo)
    if len(articles) < 10:
        print(f"WARNING: only {len(articles)} articles found; aborting.")
        return 1
    print(f"Scanned {len(articles)} articles. Newest: {articles[0]['date']} — {articles[0]['title']}")

    build_news_index(repo, articles)
    print("  news/index.html")
    for label, n in build_category_pages(repo, articles):
        print(f"  news/{CATEGORIES[label]}/index.html  ({n} stories)")
    print(f"  best/index.html  ({build_best_index(repo)} guides)")
    update_homepage(repo, articles)
    print("  index.html (homepage sections refreshed)")
    print(f"  sitemap.xml ({build_sitemap(repo, articles)} urls)")
    return 0


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    sys.exit(main(repo))
