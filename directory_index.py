"""Keep the directory's browse pages aligned with its published profiles."""

from html import escape, unescape
from pathlib import Path
import re


CATEGORIES = (
    "food-and-drink", "tech", "health-and-wellness", "real-estate",
    "arts-and-culture", "retail", "professional-services",
    "trades-and-services", "education", "finance", "automotive",
)

# Old profile URLs stay available through permanent redirects in vercel.json.
ALIASES = {
    "construction-junction-retail": "construction-junction",
    "gaucho-parrilla-argentina": "gaucho-parrilla",
    "s-and-w-randall-toyes-downtown": "sw-randall-toyes",
    "upmc-health-system": "upmc",
}

# These former restaurants are retained for historical links, but should not
# appear among businesses readers can visit today.
INACTIVE = {"cure-restaurant", "smallman-galley", "superior-motors"}

# Their stated websites either fail DNS or resolve to a parked domain, and a
# Pittsburgh business match was not corroborated. Keep URLs for corrections.
UNVERIFIED = {
    "alphabet-city-coffee", "arsenal-outfitters", "bodhi-health-wellness",
    "circuitspark-labs", "pavement-boutique", "pgh-software-co",
    "pittsburgh-title-partners", "steel-city-finance", "vector-capital-advisors",
}

# Only profiles with a checked primary source and a rewritten factual summary
# are promoted in browse pages and the sitemap. Other legacy profiles stay
# reachable for corrections without presenting their unsourced narratives.
VERIFIED = {
    "baum-boulevard-automotive", "carnegie-robotics", "chatham-university", "construction-junction",
    "de-fer-coffee", "dollar-bank", "franco-associates", "gaucho-parrilla",
    "gecko-robotics", "pamelas-diner", "pennsylvania-macaroni", "petuum",
    "pj-dick", "pnc-financial-services", "point-breeze-vet",
    "pittsburgh-cultural-trust", "primanti-brothers", "steel-city-boxing",
    "sw-randall-toyes", "upmc", "walnut-capital",
}
VERIFIED_CATEGORY = {
    "baum-boulevard-automotive": "automotive",
    "carnegie-robotics": "tech", "chatham-university": "education",
    "construction-junction": "retail", "de-fer-coffee": "food-and-drink",
    "dollar-bank": "finance", "franco-associates": "professional-services",
    "gaucho-parrilla": "food-and-drink", "gecko-robotics": "tech",
    "pamelas-diner": "food-and-drink", "pennsylvania-macaroni": "food-and-drink",
    "petuum": "tech", "pj-dick": "trades-and-services",
    "pnc-financial-services": "finance", "point-breeze-vet": "health-and-wellness",
    "pittsburgh-cultural-trust": "arts-and-culture",
    "primanti-brothers": "food-and-drink", "steel-city-boxing": "health-and-wellness",
    "sw-randall-toyes": "retail", "upmc": "health-and-wellness",
    "walnut-capital": "real-estate",
}
PENDING_REVIEW = {
    p.parent.name for p in (Path(__file__).resolve().parent / "directory").glob("*/index.html")
    if p.parent.name not in set(CATEGORIES) | set(ALIASES) | INACTIVE | UNVERIFIED | VERIFIED
}
EXCLUDED = set(ALIASES) | INACTIVE | UNVERIFIED | PENDING_REVIEW

CARD = re.compile(r'\s*<a class="biz-card" href="/directory/([^/]+)/">.*?</a>', re.S)
EXTRA_START = "<!-- DIRECTORY_EXTRA_START -->"
EXTRA_END = "<!-- DIRECTORY_EXTRA_END -->"


def clean_cards(source):
    """Remove repeated profile cards and decode escaped visual line breaks."""
    source = CARD.sub(lambda m: "" if m.group(1) in EXCLUDED else m.group(0), source)
    return source.replace("&lt;br&gt;", "<br>").replace("&amp;amp;", "&amp;")


def add_sourced_cards(source, root, slugs):
    """Give each checked profile a discoverable card exactly once."""
    existing = set(CARD.findall(source))
    cards = []
    for slug in sorted(set(slugs) - existing):
        name = profile_name(root / slug / "index.html")
        cards.append(f'    <a class="biz-card" href="/directory/{escape(slug)}/">'
                     f'<div class="biz-name">{escape(name)}</div>'
                     '<div class="biz-owner">Source-checked profile</div></a>')
    if not cards:
        return source
    grid = re.search(r'<div class="biz-grid"[^>]*>', source)
    if not grid:
        raise ValueError("Missing directory card grid")
    return source[:grid.end()] + "\n" + "\n".join(cards) + source[grid.end():]


def profile_name(page):
    match = re.search(r"<title>(.*?)</title>", page.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"Directory profile has no title: {page}")
    name = match.group(1).split(" | ", 1)[0]
    return unescape(unescape(name)).strip()


def update(repo):
    root = Path(repo) / "directory"
    counts = {}
    for slug in CATEGORIES:
        page = root / slug / "index.html"
        source = clean_cards(page.read_text(encoding="utf-8"))
        source = CARD.sub(lambda m: "" if m.group(1) in VERIFIED and VERIFIED_CATEGORY[m.group(1)] != slug else m.group(0), source)
        source = add_sourced_cards(source, root, (name for name, category in VERIFIED_CATEGORY.items() if category == slug))
        count = len(CARD.findall(source))
        source = re.sub(r'(<p class="hub-count">)\d+ businesses listed(</p>)',
                        rf'\g<1>{count} featured businesses\2', source, count=1)
        source = re.sub(r'(<p class="hub-count">)\d+ featured businesses(</p>)',
                        rf'\g<1>{count} featured businesses\2', source, count=1)
        page.write_text(source, encoding="utf-8")
        counts[slug] = count

    page = root / "index.html"
    source = clean_cards(page.read_text(encoding="utf-8"))
    source = add_sourced_cards(source, root, VERIFIED)
    featured = set(CARD.findall(source))
    profiles = []
    for profile in root.glob("*/index.html"):
        slug = profile.parent.name
        if slug in VERIFIED:
            profiles.append((profile_name(profile), slug))
    remaining = sorted(((name, slug) for name, slug in profiles if slug not in featured),
                       key=lambda item: item[0].casefold())
    links = "\n".join(
        f'    <a href="/directory/{escape(slug)}/">{escape(name)}</a>'
        for name, slug in remaining
    )
    block = (f'{EXTRA_START}\n'
             f'  <h2 class="section-head">More Business Profiles A-Z</h2>\n'
             f'  <div class="more-profile-grid" id="more-businesses">\n{links}\n  </div>\n'
             f'{EXTRA_END}') if remaining else f'{EXTRA_START}\n{EXTRA_END}'
    if EXTRA_START in source:
        source = re.sub(re.escape(EXTRA_START) + r'.*?' + re.escape(EXTRA_END),
                        lambda _: block, source, count=1, flags=re.S)
    else:
        source = source.replace('  <section class="dir-footer">',
                                block + '\n\n  <section class="dir-footer">', 1)

    total = len(profiles)
    source = re.sub(r'(<div class="dir-stat-num">)\d+(</div>)',
                    rf'\g<1>{total}\2', source, count=1)
    source = re.sub(r'<title>.*?</title>',
                    f'<title>Pittsburgh Business Directory | {total} Profiles | The Pittsburgh Wire</title>',
                    source, count=1)
    source = re.sub(r'(<meta name="description" content=")[^"]+',
                    rf'\g<1>Browse {total} Pittsburgh business profiles, including local restaurants, shops, service providers, and organizations.',
                    source, count=1)
    source = re.sub(r'(<meta property="og:title" content=")[^"]+',
                    rf'\g<1>Pittsburgh Business Directory | {total} Profiles', source, count=1)
    source = re.sub(r'(<meta property="og:description" content=")[^"]+',
                    rf'\g<1>Explore {total} Pittsburgh business profiles in The Pittsburgh Wire directory.',
                    source, count=1)
    source = re.sub(r'("description": ")Directory of \d+ Pittsburgh business profiles\.',
                    rf'\g<1>Directory of {total} Pittsburgh business profiles.', source, count=1)
    source = re.sub(r'("description": ")[^"]+ businesses across 11 categories\.',
                    rf'\g<1>Directory of {total} Pittsburgh business profiles.', source, count=1)
    source = re.sub(r'(<p class="dir-hero-desc">).*?(</p>)',
                    rf'\g<1>Explore Pittsburgh business profiles, from restaurants and shops to local services and organizations. Browse featured categories or search all profiles below.\2',
                    source, count=1, flags=re.S)
    source = source.replace('<div class="dir-stat-label">Businesses</div>',
                            '<div class="dir-stat-label">Business Profiles</div>', 1)
    source = source.replace('<div class="dir-stat-label">Categories</div>',
                            '<div class="dir-stat-label">Featured Categories</div>', 1)
    source = re.sub(r'\s*<div class="dir-stat">\s*<div class="dir-stat-num">41</div>\s*<div class="dir-stat-label">Neighborhoods</div>\s*</div>',
                    '', source, count=1)
    source = source.replace('All Businesses A-Z', 'Featured Businesses', 1)
    source = source.replace('Featured Businesses A-Z', 'Featured Businesses', 1)
    source = source.replace('    .biz-card:hover { border-color: var(--gold); }',
        '    .biz-card:hover { border-color: var(--gold); }\n'
        '    .more-profile-grid { max-width:1200px; margin:0 auto; padding:0 28px 48px; display:grid; grid-template-columns:repeat(3,1fr); gap:2px; }\n'
        '    .more-profile-grid a { display:block; background:var(--steel); border:1px solid var(--border); padding:14px 18px; font-family:\'Source Serif 4\',Georgia,serif; }\n'
        '    .more-profile-grid a:hover { border-color:var(--gold); color:var(--gold); }', 1) if '.more-profile-grid {' not in source else source
    source = source.replace('.biz-grid { grid-template-columns: 1fr; }',
                            '.biz-grid, .more-profile-grid { grid-template-columns: 1fr; }', 1)
    for slug, count in counts.items():
        source = re.sub(r'(<a class="cat-card" href="/directory/' + re.escape(slug) + r'/">.*?<div class="cat-count">).*?(</div>)',
                        rf'\g<1>{count} featured\2', source, count=1, flags=re.S)
        source = re.sub(r'(<a href="/directory/' + re.escape(slug) + r'/">[^<]*?) \(\d+\)(</a>)',
                        rf'\g<1> ({count})\2', source, count=1)
    page.write_text(source, encoding="utf-8")
    # Retired and unverified profiles should not be recommended from another
    # profile's "related" section, even though their old URLs stay reachable.
    excluded = EXCLUDED
    related_card = re.compile(r'\s*<a class="related-card" href="/directory/([^/]+)/">.*?</a>', re.S)
    verified_labels = {
        "franco-associates": ("Franco Associates", "Commercial masonry and restoration · Pittsburgh area"),
        "point-breeze-vet": ("Point Breeze Veterinary Clinic", "Founded in 1977 · Point Breeze"),
        "steel-city-boxing": ("Steel City Boxing Association", "Youth mentoring · Spring Hill"),
    }
    for profile in root.glob("*/index.html"):
        if profile.parent.name in CATEGORIES:
            continue
        html = profile.read_text(encoding="utf-8")
        def related_replacement(match):
            slug = match.group(1)
            if slug in excluded:
                return ""
            if slug in verified_labels:
                name, detail = verified_labels[slug]
                return re.sub(r'(<div class="related-name">).*?(</div>)',
                              lambda m: m.group(1) + escape(name) + m.group(2),
                              re.sub(r'(<div class="related-owner">).*?(</div>)',
                                     lambda m: m.group(1) + escape(detail) + m.group(2),
                                     match.group(0), count=1, flags=re.S), count=1, flags=re.S)
            return match.group(0)
        cleaned = related_card.sub(related_replacement, html)
        slug = profile.parent.name
        if slug in VERIFIED and re.search(r'<div class="related-grid">\s*</div>', cleaned):
            peers = [other for other in sorted(VERIFIED)
                     if other != slug and VERIFIED_CATEGORY[other] == VERIFIED_CATEGORY[slug]][:3]
            cards = "\n".join(
                f'<a class="related-card" href="/directory/{escape(other)}/">'
                f'<div class="related-name">{escape(profile_name(root / other / "index.html"))}</div></a>'
                for other in peers
            )
            cleaned = re.sub(r'<div class="related-grid">\s*</div>',
                             lambda _: f'<div class="related-grid">{cards}</div>', cleaned, count=1)
            if not peers:
                cleaned = cleaned.replace('class="related-head">More Pittsburgh Businesses',
                                          'class="related-head">Browse the Directory', 1)
        if cleaned != html:
            profile.write_text(cleaned, encoding="utf-8")
    return len(featured), len(remaining), total
