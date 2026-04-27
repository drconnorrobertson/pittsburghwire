#!/usr/bin/env python3
"""
update_homepage.py -- The Pittsburgh Wire Homepage Regenerator

Scans /news/ for all published articles, sorts by date, and regenerates
the dynamic content sections of index.html while preserving the exact
design, CSS, and layout.

Usage:
    python3 update_homepage.py                  # run from repo root
    python3 update_homepage.py /path/to/repo    # specify repo path

Sections updated:
    - Ticker/marquee bar (top 6 headlines, repeated twice)
    - Top Story (lead-grid: main + sidebar with 2 stories)
    - Three-column story row (3 stories)
    - Dark belt / Development & Real Estate (4 stories)
    - People of Pittsburgh (3 spotlights)
    - "More from The Wire" card grid (top 30 articles)
"""

import re
import os
import sys
import html as html_mod

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
DEFAULT_IMAGES = {
    "Business":      "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80",
    "Technology":    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&q=80",
    "Real Estate":   "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&q=80",
    "Development":   "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=400&q=80",
    "Dining":        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80",
    "Community":     "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=400&q=80",
    "People":        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80",
    "Healthcare":    "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&q=80",
    "Hospitality":   "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&q=80",
    "Neighborhoods": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&q=80",
}
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80"

MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}
MONTH_NUMS = {v: k for k, v in MONTH_NAMES.items()}

# ---------------------------------------------------------------------------
# ARTICLE SCANNER
# ---------------------------------------------------------------------------
def scan_articles(repo_dir):
    """Scan /news/ subdirectories and return a list of article dicts sorted newest-first."""
    news_dir = os.path.join(repo_dir, "news")
    articles = []

    for slug in os.listdir(news_dir):
        fpath = os.path.join(news_dir, slug, "index.html")
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # --- Date (ISO) ---
        m = re.search(r'content="(\d{4}-\d{2}-\d{2})', content)
        if m:
            date = m.group(1)
        else:
            m2 = re.search(
                r'(January|February|March|April|May|June|July|August|'
                r'September|October|November|December)\s+(\d+),\s+(\d{4})', content)
            if m2:
                date = f"{m2.group(3)}-{MONTH_NUMS[m2.group(1)]}-{int(m2.group(2)):02d}"
            else:
                continue

        # --- Title ---
        tm = re.search(r'<title>([^|<]+)', content)
        title = tm.group(1).strip() if tm else slug.replace("-", " ").title()

        # --- Description ---
        dm = re.search(r'name="description" content="([^"]+)"', content)
        desc = dm.group(1).strip() if dm else ""

        # --- OG Image ---
        im = re.search(r'property="og:image" content="([^"]+)"', content)
        img = im.group(1).strip() if im else ""

        # --- Category ---
        cm = re.search(r'class="story-label">([^<]+)', content)
        cat = cm.group(1).strip() if cm else "Business"

        # --- Byline ---
        bm = re.search(r'By <span>([^<]+)', content)
        byline = bm.group(1).strip() if bm else ""

        # --- Display date ---
        parts = date.split("-")
        display_date = f"{MONTH_NAMES[parts[1]]} {int(parts[2])}, {parts[0]}"

        articles.append({
            "slug": slug, "date": date, "title": title, "desc": desc,
            "img": img, "cat": cat, "byline": byline, "display_date": display_date
        })

    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles


def thumb(article):
    """Return a 400w thumbnail URL for an article."""
    if article["img"]:
        return article["img"].replace("w=1200", "w=400")
    return DEFAULT_IMAGES.get(article["cat"], FALLBACK_IMAGE)


def hero_img(article):
    """Return an 800w hero image URL for an article."""
    if article["img"]:
        return article["img"].replace("w=1200", "w=800").replace("w=400", "w=800")
    return DEFAULT_IMAGES.get(article["cat"], FALLBACK_IMAGE).replace("w=400", "w=800")


# ---------------------------------------------------------------------------
# HTML GENERATORS
# ---------------------------------------------------------------------------
def gen_ticker(articles):
    top = articles[:6]
    spans = ""
    for a in top:
        spans += f'      <span>{html_mod.escape(a["title"])}</span>\n'
    # Repeat first two for seamless loop
    for a in top[:2]:
        spans += f'      <span>{html_mod.escape(a["title"])}</span>\n'
    return spans


def gen_lead(articles):
    """Top story (index 0), sidebar image, sidebar stories (index 1-2)."""
    a0, a1, a2 = articles[0], articles[1], articles[2]
    return f"""
        <div class="lead-main">
          <span class="story-label">{a0["cat"]}</span>
          <h2 class="lead-headline">
            <a href="/news/{a0["slug"]}">{html_mod.escape(a0["title"])}</a>
          </h2>
          <p class="lead-deck">{html_mod.escape(a0["desc"])}</p>
          <p class="byline">{a0["display_date"]}</p>
        </div>
        <div class="lead-sidebar">
          <img src="{hero_img(a0)}" alt="" onerror="this.style.display='none'" style="width:100%;height:200px;object-fit:cover;display:block;" />
          <p class="img-caption">Photo: Unsplash</p>
          <div class="sidebar-story">
            <span class="story-label">{a1["cat"]}</span>
            <p class="sidebar-headline"><a href="/news/{a1["slug"]}">{html_mod.escape(a1["title"])}</a></p>
            <p class="sidebar-deck">{html_mod.escape(a1["desc"][:160])}</p>
          </div>
          <div class="sidebar-story">
            <span class="story-label">{a2["cat"]}</span>
            <p class="sidebar-headline"><a href="/news/{a2["slug"]}">{html_mod.escape(a2["title"])}</a></p>
            <p class="sidebar-deck">{html_mod.escape(a2["desc"][:160])}</p>
          </div>
        </div>
      """


def gen_threecol(articles):
    """Three-column row: articles at index 3, 4, 5."""
    out = ""
    for a in articles[3:6]:
        out += f"""
        <div class="col-story">
          <span class="story-label">{a["cat"]}</span>
          <p class="col-headline"><a href="/news/{a["slug"]}">{html_mod.escape(a["title"])}</a></p>
          <p class="col-deck">{html_mod.escape(a["desc"][:180])}</p>
          <p class="byline">{a["display_date"]}</p>
        </div>"""
    return out + "\n      "


def gen_belt(articles):
    """Dark belt: articles at index 6, 7, 8, 9."""
    out = ""
    for a in articles[6:10]:
        cat_label = a["cat"] if a["cat"] != "Business" else "Business"
        out += f"""
          <div class="belt-item">
            <div class="belt-cat">{cat_label}</div>
            <p class="belt-headline"><a href="/news/{a["slug"]}" style="color:inherit">{html_mod.escape(a["title"])}</a></p>
            <p class="belt-byline">{a["display_date"]}</p>
          </div>"""
    return out + "\n        "


def gen_people(articles):
    """People section: spotlight top 3 articles (index 0-2) as person cards."""
    out = ""
    for a in articles[:3]:
        # Generate initials from first two words of title
        words = a["title"].split()
        initials = "".join(w[0] for w in words[:2] if w[0].isalpha()).upper()
        # Use byline name if available, else title snippet
        name = a["byline"] if a["byline"] else words[0] + (" " + words[1] if len(words) > 1 else "")
        out += f"""
        <div class="person-card">
          <div class="person-avatar">{initials}</div>
          <p class="person-name">{html_mod.escape(name)}</p>
          <p class="person-title">{a["cat"]}</p>
          <p class="person-desc">{html_mod.escape(a["desc"][:200])}</p>
        </div>"""
    return out + "\n      "


def gen_more_cards(articles):
    """More from The Wire: top 30 articles as cards."""
    out = ""
    for a in articles[:30]:
        byline_str = f"By {html_mod.escape(a['byline'])} - " if a["byline"] else ""
        out += f"""          <div class="more-card">
            <img class="more-card-thumb" src="{thumb(a)}" alt="" loading="lazy" onerror="this.style.display='none'" />
            <span class="more-card-label">{a["cat"]}</span>
            <p class="more-card-headline"><a href="/news/{a["slug"]}">{html_mod.escape(a["title"])}</a></p>
            <p class="more-card-date">{byline_str}{a["display_date"]}</p>
          </div>
"""
    return out


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def update_homepage(repo_dir):
    index_path = os.path.join(repo_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    articles = scan_articles(repo_dir)
    if len(articles) < 10:
        print(f"WARNING: Only {len(articles)} articles found. Need at least 10.")
        return

    print(f"Found {len(articles)} articles. Newest: {articles[0]['date']} - {articles[0]['title']}")

    # 1. Ticker
    m = re.search(r'(<div class="ticker-inner">)(.*?)(</div>\s*</div>\s*<!-- MAIN)', html, re.DOTALL)
    if m:
        html = html[:m.start(2)] + "\n" + gen_ticker(articles) + "    " + html[m.end(2):]

    # 2. Lead story
    m = re.search(r'(<div class="lead-grid fade-up">)(.*?)(</div>\s*</div>\s*</div>(?=\s*<!-- 3-COL))', html, re.DOTALL)
    if m:
        html = html[:m.start(2)] + gen_lead(articles) + "\n      " + html[m.end(2):]

    # 3. Three-col
    m = re.search(r'(<div class="three-col fade-up delay-1">)(.*?)(</div>\s*</div>(?=\s*</div>\s*<!-- DARK BELT))', html, re.DOTALL)
    if m:
        html = html[:m.start(2)] + gen_threecol(articles) + html[m.end(2):]

    # 4. Belt
    m = re.search(r'(<div class="belt-grid">)(.*?)(</div>\s*</div>\s*</div>\s*(?=<div class="container">))', html, re.DOTALL)
    if m:
        html = html[:m.start(2)] + gen_belt(articles) + html[m.end(2):]

    # 5. People
    m = re.search(r'(<div class="people-grid fade-up delay-2">)(.*?)(</div>\s*<div class="rule-double">)', html, re.DOTALL)
    if m:
        html = html[:m.start(2)] + gen_people(articles) + html[m.end(2):]

    # 6. More from The Wire
    m = re.search(r'(<div class="more-grid">)(.*?)(</div>\s*</div>\s*</section>)', html, re.DOTALL)
    if m:
        html = html[:m.start(2)] + "\n" + gen_more_cards(articles) + "        " + html[m.end(2):]

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Homepage updated successfully!")
    print(f"Top story: {articles[0]['title']}")
    print(f"Sidebar: {articles[1]['title']}, {articles[2]['title']}")
    print(f"Three-col: {articles[3]['title']}, {articles[4]['title']}, {articles[5]['title']}")


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    update_homepage(repo)
