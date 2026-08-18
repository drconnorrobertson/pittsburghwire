#!/usr/bin/env python3
"""
new_post.py -- publish one article to The Pittsburgh Wire

Fills templates/article.html from a JSON spec, writes news/<slug>/index.html,
then runs build_site.py so the homepage, the /news/ archive, the section
indexes, and the sitemap all pick up the new story.

The Pittsburgh Wire is a text-only publication. This script never emits an
<img> tag and refuses any body copy that contains one.

Usage:
    python3 new_post.py story.json
    cat story.json | python3 new_post.py -

story.json:
{
  "slug":     "lawrenceville-coffee-roaster-second-location",
  "headline": "Lawrenceville Coffee Roaster Opens Second Location on Butler",
  "deck":     "One-to-two sentence italic summary, 25-40 words.",
  "section":  "Business",          // Business | Real Estate | Development | People | Neighborhoods
  "byline":   "Megan Strickland",
  "date":     "2026-08-19",        // ISO; defaults to today
  "read_time": "4 min read",       // optional, estimated from the body if omitted
  "tags":     ["Lawrenceville", "Coffee", "Small Business"],
  "body":     "<p>First paragraph...</p>\\n<h2>A Subhead</h2>\\n<p>...</p>"
}

Body copy is raw HTML using the house classes: <p>, <h2>, <div class="fact-box">,
<div class="pullquote">. No images, ever.
"""

import json
import os
import re
import subprocess
import sys
import html as H
from datetime import date as _date

REPO = os.path.dirname(os.path.abspath(__file__))
SECTIONS = ["Business", "Real Estate", "Development", "People", "Neighborhoods"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def load_spec(argv):
    if len(argv) < 2:
        die("usage: new_post.py <story.json>|-")
    raw = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        die("story spec is not valid JSON: %s" % e)


def validate(spec):
    for field in ("slug", "headline", "deck", "body"):
        if not spec.get(field):
            die("missing required field: %s" % field)

    slug = spec["slug"]
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        die("slug must be lowercase words separated by single hyphens: %r" % slug)
    if os.path.exists(os.path.join(REPO, "news", slug)):
        die("news/%s already exists -- pick a different slug" % slug)

    section = spec.get("section", "Business")
    if section not in SECTIONS:
        die("section must be one of %s" % ", ".join(SECTIONS))

    body = spec["body"]
    if "<img" in body.lower() or "unsplash" in body.lower():
        die("The Pittsburgh Wire is text-only: remove the image from the body.")

    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    if words < 400:
        die("body is only %d words; articles run 500-700" % words)
    return words


def related_stories(exclude_slug, section, limit=3):
    """Recent stories, same section first, as sidebar links."""
    sys.path.insert(0, REPO)
    import build_site
    arts = [a for a in build_site.scan_articles(REPO) if a["slug"] != exclude_slug]
    same = [a for a in arts if a["cat"] == section]
    picks = (same + [a for a in arts if a not in same])[:limit]
    return picks


def render_related(picks):
    out = []
    for a in picks:
        out.append('        <div class="related-story">\n'
                   '          <div class="related-cat">%s</div>\n'
                   '          <p class="related-hed"><a href="/news/%s">%s</a></p>\n'
                   '          <div class="related-date">%s</div>\n'
                   '        </div>' % (H.escape(a["cat"]), a["slug"],
                                       H.escape(a["title"]), a["display_date"]))
    return "\n".join(out)


def render_more(picks):
    out = []
    for a in picks:
        out.append('        <div class="more-card">\n'
                   '          <div class="more-cat">%s</div>\n'
                   '          <p class="more-hed"><a href="/news/%s">%s</a></p>\n'
                   '          <div class="more-date">%s</div>\n'
                   '        </div>' % (H.escape(a["cat"]), a["slug"],
                                       H.escape(a["title"]), a["display_date"]))
    return "\n".join(out)


def main():
    spec = load_spec(sys.argv)
    words = validate(spec)

    slug = spec["slug"]
    section = spec.get("section", "Business")
    headline = spec["headline"].strip()
    deck = spec["deck"].strip()
    byline = spec.get("byline", "The Pittsburgh Wire Staff").strip()
    iso = spec.get("date") or _date.today().isoformat()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', iso):
        die("date must be YYYY-MM-DD")
    y, m, d = iso.split("-")
    display = "%s %d, %s" % (MONTHS[int(m) - 1], int(d), y)
    read_time = spec.get("read_time") or "%d min read" % max(2, round(words / 225))

    tags = spec.get("tags") or []
    tags_html = "\n".join('        <span class="tag">%s</span>' % H.escape(t) for t in tags)

    picks = related_stories(slug, section, 6)

    tpl = open(os.path.join(REPO, "templates", "article.html"), encoding="utf-8").read()
    out = tpl
    for token, value in [
        ("{{SLUG}}", slug),
        ("{{SECTION}}", H.escape(section)),
        ("{{HEADLINE_SHORT}}", H.escape(headline[:58] + ("&hellip;" if len(headline) > 58 else ""))),
        ("{{HEADLINE}}", H.escape(headline)),
        ("{{DECK}}", H.escape(deck)),
        ("{{BYLINE}}", H.escape(byline)),
        ("{{DATE_ISO}}", iso),
        ("{{DATE_DISPLAY}}", display),
        ("{{READ_TIME}}", H.escape(read_time)),
        ("{{TAGS}}", tags_html),
        ("{{RELATED}}", render_related(picks[:3])),
        ("{{MORE}}", render_more(picks[3:6])),
        ("{{BODY}}", spec["body"].strip()),
    ]:
        out = out.replace(token, value)

    left = re.findall(r'\{\{[A-Z_]+\}\}', out)
    if left:
        die("template placeholders left unfilled: %s" % ", ".join(sorted(set(left))))
    if "<img" in out.lower():
        die("refusing to write an article containing an image")

    d = os.path.join(REPO, "news", slug)
    os.makedirs(d)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    print("wrote news/%s/index.html  (%d words, %s)" % (slug, words, read_time))

    print("rebuilding derived pages...")
    subprocess.run([sys.executable, os.path.join(REPO, "build_site.py"), REPO], check=True)


if __name__ == "__main__":
    main()
