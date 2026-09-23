"""Refresh neighborhood discovery cards from published, relevant pages."""

from html import escape, unescape
from pathlib import Path
import json
import re

from directory_index import VERIFIED, profile_name


ALIASES = {
    "downtown": ("downtown", "golden triangle", "cultural district"),
    "hazelwood-green": ("hazelwood green", "hazelwood"),
    "hill-district": ("hill district", "lower hill"),
    "mt-washington": ("mt. washington", "mount washington"),
    "north-side": ("north side", "north shore"),
    "south-side": ("south side", "southside"),
}

# Include a business only where its location is supported by its checked
# profile or the business's own published address/location directory.
LOCAL_PROFILES = {
    "downtown": ("pittsburgh-cultural-trust", "pnc-financial-services", "gaucho-parrilla"),
    "lawrenceville": ("carnegie-robotics",),
    "north-side": ("gecko-robotics",),
    "shadyside": ("walnut-capital",),
    "strip-district": ("pamelas-diner", "pennsylvania-macaroni", "primanti-brothers"),
}


def replace_once(source, start, end, replacement, page):
    a = source.find(start)
    b = source.find(end, a + len(start)) if a >= 0 else -1
    if a < 0 or b < 0:
        raise ValueError(f"Neighborhood section markers missing: {page}")
    return source[:a + len(start)] + replacement + source[b:]


def article_cards(slug, articles):
    terms = ALIASES.get(slug, (slug.replace("-", " "),))
    selected = []
    for article in articles:
        haystack = " ".join((article["title"], article["slug"].replace("-", " "))).casefold()
        if not article["slug"].startswith("best-") and any(term in haystack for term in terms):
            selected.append(article)
        if len(selected) == 8:
            break
    cards = []
    for item in selected:
        description = item["desc"]
        if len(description) > 155:
            description = description[:155].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
        cards.append(f'''\n        <a href="/news/{escape(item["slug"])}" class="article-card">
          <div class="article-card-section">{escape(item["cat"])}</div>
          <div class="article-card-title">{escape(item["title"])}</div>
          <div class="article-card-desc">{escape(description)}</div>
          <div class="article-card-date">{escape(item["display_date"])}</div>
        </a>''')
    if not cards:
        cards.append('\n      <p class="empty-state">No neighborhood-specific reports are published yet. '
                     '<a href="/news/">Browse all Pittsburgh stories</a>.</p>')
    return selected, "".join(cards) + "\n    "


def business_cards(slug, repo):
    checked = list(LOCAL_PROFILES.get(slug, ()))
    cards = []
    for profile_slug in checked:
        if profile_slug not in VERIFIED:
            raise ValueError(f"Unverified profile in neighborhood mapping: {profile_slug}")
        profile = Path(repo) / "directory" / profile_slug / "index.html"
        html = profile.read_text(encoding="utf-8")
        description = re.search(r'<meta name="description" content="([^"]*)"', html)
        desc = unescape(description.group(1)) if description else "Read the checked business profile."
        if len(desc) > 155:
            desc = desc[:155].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
        cards.append(f'''\n        <a href="/directory/{escape(profile_slug)}" class="biz-card">
          <div class="biz-card-top"><div class="biz-icon">&#9670;</div><div class="biz-cat-badge">Verified profile</div></div>
          <div class="biz-name">{escape(profile_name(profile))}</div>
          <div class="biz-desc">{escape(desc)}</div>
        </a>''')
    if not cards:
        cards.append('\n      <p class="empty-state">No source-checked profiles are listed here yet. '
                     '<a href="/directory/">Browse the Pittsburgh business directory</a>.</p>')
    return checked, "".join(cards) + "\n    "


def update(repo, articles):
    root = Path(repo) / "neighborhoods"
    report = []
    for page in sorted(root.glob("*/index.html")):
        slug = page.parent.name
        source = page.read_text(encoding="utf-8")
        name_match = re.search(r'<h1 class="hero-headline">([^<]+)</h1>', source)
        if not name_match:
            raise ValueError(f"Neighborhood heading missing: {page}")
        name = unescape(name_match.group(1))
        news, news_markup = article_cards(slug, articles)
        businesses, business_markup = business_cards(slug, repo)
        description = (f"Explore {name} in the Pittsburgh area: neighborhood context, "
                       "recent local reporting, and source-checked business profiles.")
        for attribute in ('name="description"', 'property="og:description"',
                          'name="twitter:description"'):
            source, count = re.subn(r'(<meta ' + re.escape(attribute) + r' content=")[^"]*(" />)',
                                    lambda m: m.group(1) + escape(description, quote=True) + m.group(2),
                                    source, count=1)
            if count != 1:
                raise ValueError(f"Neighborhood description missing: {page}")
        source, count = re.subn(r'(<p class="hero-sub">).*?(</p>)',
                                lambda m: m.group(1) + escape(description) + m.group(2),
                                source, count=1)
        if count != 1:
            raise ValueError(f"Neighborhood summary missing: {page}")
        source, count = re.subn(r'("@type": "Place",\s*"name": "[^"]+",\s*"description": )"[^"]*"',
                                lambda m: m.group(1) + json.dumps(description), source, count=1)
        if count != 1:
            raise ValueError(f"Neighborhood structured description missing: {page}")
        if slug == "homestead":
            source = source.replace('"addressLocality": "Pittsburgh"',
                                    '"addressLocality": "Homestead"', 1)
        source = replace_once(source, '<div class="article-grid">',
                              '</div>\n\n    <div class="section-label">', news_markup, page)
        source = replace_once(source, '<div class="biz-grid">',
                              '</div>\n\n    <div class="nearby-section">', business_markup, page)
        stat_counts = iter((len(news), len(businesses)))
        source = re.sub(r'(<span class="stat-num">)\d+(</span>)',
                        lambda m: m.group(1) + str(next(stat_counts)) + m.group(2),
                        source, count=2)
        stat_labels = iter(("Article" if len(news) == 1 else "Articles",
                            "Business" if len(businesses) == 1 else "Businesses"))
        source = re.sub(r'(<span class="stat-label">)[^<]+(</span>)',
                        lambda m: m.group(1) + next(stat_labels) + m.group(2),
                        source, count=2)
        labels = iter((f'{len(news)} Article{"s" if len(news) != 1 else ""}',
                       f'{len(businesses)} Business{"es" if len(businesses) != 1 else ""}'))
        source = re.sub(r'(<span class="section-label-count">)[^<]+(</span>)',
                        lambda m: m.group(1) + next(labels) + m.group(2), source, count=2)
        source = re.sub(r'<span class="section-label-text">(.*?)</span>',
                        r'<h2 class="section-label-text">\1</h2>', source)
        if 'name="date-modified"' not in source:
            source = source.replace('  <meta name="robots"',
                                    '  <meta name="date-modified" content="2026-09-22" />\n  <meta name="robots"', 1)
        page.write_text(source, encoding="utf-8")
        report.append((slug, len(news), len(businesses)))
    return report
