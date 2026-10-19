"""Intent-specific collections of published, researched comparison guides."""
import json
import re
from html import escape as esc
from pathlib import Path

# Explicit topic assignments avoid turning ordinary news into recommendations.
TOPICS = {
    'home-services': {
        'title': 'Pittsburgh Home Services: Compare Local Providers',
        'intro': 'Plan a repair, move or improvement with our researched Pittsburgh-area provider shortlists. Start with the job you need done, then compare the documented services and estimate process in the individual guide.',
        'advice': 'Define the scope, property location and timing before requesting estimates. Ask each provider for a written scope, exclusions, applicable license and insurance details, and who handles follow-up. Compare equivalent work rather than the lowest headline quote.',
        'terms': ['roofing-contractors', 'plumbers', 'pest-control', 'moving-companies', 'landscapers', 'hvac-companies', 'home-organizers', 'electricians', 'handyman-services', 'self-storage-options', 'diy-resources', 'tile-showrooms', 'flooring-installation', 'basement-waterproofing', 'home-inspectors', 'fence-installation', 'garage-door-service', 'area-rug-cleaning', 'appliance-repair', 'furniture-repair-upholstery', 'junk-removal', 'locksmiths', 'window-cleaners', 'fireplace-showrooms'],
    },
    'business-services': {
        'title': 'Pittsburgh Business Services: Compare Local Options',
        'intro': 'Find a practical starting point for a Pittsburgh business project: a website, print materials, accounting support, workspace or commercial cleaning. Each linked guide names providers and links to the sources behind its service descriptions.',
        'advice': 'Write down your deliverables, budget range and deadline. Ask about onboarding, ongoing charges, ownership of completed work, cancellation terms and the person responsible for your account. Accounting and other professional engagements need a scope tailored to your business.',
        'terms': ['web-design-agencies', 'print-and-sign-shops', 'accountants-tax', 'coworking-spaces', 'commercial-cleaners', 'translation-services', 'computer-repair'],
    },
    'things-to-do': {
        'title': 'Pittsburgh Things to Do: Local Lists and Planning Guides',
        'intro': 'Compare Pittsburgh-area outings by the kind of day you want: a museum visit, walking tour, creative class, game night or film screening. These shortlists help you move from an idea to the official booking or visitor information.',
        'advice': 'Check the official calendar for your specific date before making plans. For groups, confirm capacity, private versus shared admission, age restrictions and accessibility needs. Hours, seasonal programs and ticket availability can change after a guide is published.',
        'terms': ['walking-tours', 'escape-rooms', 'farmers-markets', 'bowling-three', 'astronomy-planetarium', 'movie-theaters', 'record-stores', 'museums-rainy', 'gardens-park', 'craft-classes', 'pinball-arcade', 'chocolate-shops', 'buffet-restaurants', 'coffee-shops', 'indoor-pickleball', 'archery-lessons', 'indoor-climbing', 'laser-tag', 'adult-language-classes', 'cooking-classes', 'adult-dance-classes', 'pottery-classes'],
    },
    'events-and-personal-services': {
        'title': 'Pittsburgh Event and Personal Services: Local Comparisons',
        'intro': 'Explore researched shortlists for events, personal appointments and pet care around Pittsburgh. Use the individual comparisons to narrow your options by services, location and the questions to ask before booking.',
        'advice': 'For an event, confirm the date, guest count, minimum spend, deposit and cancellation policy. For appointments or pet care, ask about intake requirements, staff qualifications relevant to the service, scheduling and what the quoted price includes. A published service menu does not establish current availability.',
        'terms': ['caterers', 'event-venues', 'wedding-photographers', 'florists-delivery', 'hair-salons', 'day-spas', 'gyms', 'pet-grooming', 'dog-daycare', 'bike-repair', 'auto-repair', 'running-shoe-fitting', 'auto-glass', 'school-instrument-rentals', 'watch-repair', 'sewing-machine-repair', 'clothing-alterations', 'piano-tuning', 'barbershops', 'dog-training', 'tutoring-centers', 'dry-cleaners', 'driving-lessons'],
    },
}


def selected(articles, topic):
    return [a for a in articles if any(term in a['slug'] for term in topic['terms']) and
            (a['slug'].startswith(('best-', 'pittsburgh-')))]


def write(repo, page_shell, articles):
    from build_site import flat_archive, SITE
    cards = []
    extras = []
    for slug, topic in TOPICS.items():
        guides = selected(articles, topic)
        if len(guides) < 3:
            raise ValueError(f'Comparison hub {slug} needs at least three published guides')
        url = f'{SITE}/best/{slug}/'
        nav = ' · '.join(f'<a href="/best/{other}/">{esc(t["title"].split(":")[0])}</a>' for other, t in TOPICS.items() if other != slug)
        body = f'''<div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/best/">Best Of</a></div>
<div class="page-head"><span class="page-eyebrow">Local comparisons</span><h1 class="page-title">{esc(topic['title'])}</h1><p class="page-deck">{esc(topic['intro'])}</p><p class="page-count">{len(guides)} published guides</p></div>
<main class="archive"><h2 class="month-head">How to compare your options</h2><p>{esc(topic['advice'])}</p>
<h2 class="month-head">Choose a guide</h2>{flat_archive(guides)}
<h2 class="month-head">How these lists work</h2><p>These are editorial shortlists, not exhaustive directories or a rating of every Pittsburgh provider. Read each guide for its sources, publication date, selection rationale and any publisher relationship disclosure. Listings do not imply a personal visit, independent service test or guaranteed result.</p>
<p>Looking for a broader selection? <a href="/directory/">Browse the business directory</a>. <a href="/contact/">Send a correction or suggest an addition</a>.</p>
<h2 class="month-head">Explore more comparisons</h2><p>{nav}</p></main>'''
        schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': topic['title'], 'url': url,
                  'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': a['title'], 'url': f'{SITE}/news/{a["slug"]}'} for i, a in enumerate(guides, 1)]}}
        out = page_shell(topic['title'] + ' | The Pittsburgh Wire', topic['intro'], url, body, active_nav='/best/')
        out = out.replace('</head>', '<meta name="wire:curated-guide" content="true" />\n<script type="application/ld+json">' + json.dumps(schema).replace('<', '\\u003c') + '</script>\n</head>')
        dest = Path(repo) / 'best' / slug / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out)
        cards.append(f'<article class="story-card"><h2 class="card-headline"><a href="/best/{slug}/">{esc(topic["title"])}</a></h2><p>{esc(topic["intro"])}</p><p>{len(guides)} guides</p></article>')
        for article in guides:
            path = Path(repo) / 'news' / article['slug'] / 'index.html'
            content = path.read_text()
            content = re.sub(r'<!-- comparison-hub -->.*?<!-- /comparison-hub -->\n?', '', content, flags=re.S)
            link = f'<!-- comparison-hub --><p>Explore more: <a href="/best/{slug}/">{esc(topic["title"])}</a>.</p><!-- /comparison-hub -->\n'
            marker = '<div class="article-tags"'
            if marker in content:
                content = content.replace(marker, link + marker, 1)
            elif '</article>' in content:
                content = content.replace('</article>', link + '</article>', 1)
            else:
                raise ValueError(f'Missing article container: {path}')
            if content != path.read_text():
                path.write_text(content)
        extras.extend((a['slug'], 'Local comparisons', a['title'], a['desc']) for a in guides)
    return '<h2 class="month-head">Compare by topic</h2><div class="card-grid">' + ''.join(cards) + '</div>', extras
