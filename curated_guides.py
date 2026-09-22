"""Source-backed Best of guides. Each entry must be checked before publishing."""

from html import escape
from pathlib import Path


GUIDES = {
    "coffee-shops-in-lawrenceville": {
        "title": "Coffee Shops in Lawrenceville: Five Local Picks",
        "description": "Five Lawrenceville coffee shops with distinct reasons to visit, verified addresses, and links to each business's own website.",
        "deck": "A useful cup depends on what you want from the stop. These five Lawrenceville cafes cover focused espresso, Vietnamese coffee, pastries, and places to linger.",
        "intro": "Each place below has a Lawrenceville address published on its own website. The picks cover different kinds of coffee stops rather than ranking one cafe above another. Check the linked business site for current hours and menus before visiting.",
        "places": [
            ("Espresso a Mano", "3623 Butler Street", "For a focused espresso stop", "A neighborhood espresso bar on Butler Street with a second Pittsburgh location. Its own site lists the Lawrenceville address and current service details.", "https://espressoamano.com/"),
            ("Ineffable Cà Phê", "3920 Penn Avenue", "For Vietnamese coffee and a longer visit", "The Lawrenceville cafe serves Vietnamese coffee and offers indoor and outdoor seating. Its site also lists food and ordering options.", "https://ineffablecaphe.com/"),
            ("Constellation Coffee", "4059 Penn Avenue", "For a coffee-focused menu", "Constellation describes itself as an espresso bar for fine coffee and tea. Its website posts current drinks and notes about its garden seating.", "https://www.constellationcoffeepgh.com/"),
            ("Inkwell Coffee House", "4419 Butler Street", "For coffee with breakfast or a pastry", "Inkwell pairs coffee sourced from De Fer with biscuit sandwiches and pastries. Its site publishes the Butler Street location and menu highlights.", "https://www.inkwellpgh.com/"),
            ("Convive Coffee Roastery", "4032 Butler Street", "For an evening coffee option", "Convive lists its Lawrenceville cafe on Butler Street and publishes hours that extend into the evening. Confirm the schedule on its site before making plans.", "https://www.convivecoffee.com/coming-soon"),
        ],
    },
    "restaurants-in-strip-district": {
        "title": "Strip District Restaurants: Five Different Ways to Eat",
        "description": "Five verified Strip District dining options, from Italian pasta and Argentine cooking to a food hall, with addresses and official links.",
        "deck": "The Strip District has room for a quick group lunch, a long dinner, and almost anything between. These five places make the choice easier by occasion and cuisine.",
        "intro": "These are distinct options, not a numerical ranking. Each business or the city's tourism organization publishes its Strip District location. Menus, vendors, and hours can change, so use the linked official site when planning a visit.",
        "places": [
            ("DiAnoia's Eatery", "2549 Penn Avenue", "For Italian pasta and a sit-down meal", "The family-run restaurant lists homemade pasta, pastries, bread, and sandwiches among its specialties. Its Penn Avenue location serves lunch and dinner.", "https://dianoiaseatery.com/"),
            ("Kaya", "2000 Smallman Street", "For island-inspired food", "Kaya's Smallman Street restaurant brings Caribbean and South American influences to the Strip. Its own site has the current menu and reservation link.", "https://www.kaya.menu/"),
            ("Bar Marco", "2216 Penn Avenue", "For wine and Italian-inspired dinner", "Bar Marco describes a menu built around Italian tradition, local farms, natural wines, and cocktails. Visit Pittsburgh lists it at 2216 Penn Avenue.", "https://www.barmarcopgh.com/"),
            ("Balvanera", "1660 Smallman Street", "For Argentine cooking", "Balvanera's Pittsburgh dining room offers dinner and weekend brunch at The Terminal. Its official location page includes reservations and service details.", "https://www.balvanerarestaurants.com/location/balvanera-pittsburgh/"),
            ("Novo Asian Food Hall", "1931 Smallman Street", "For a group with different tastes", "Novo brings several Asian kitchens and a central bar under one roof at The Terminal. Its official site lists the current vendors, menus, and accessibility details.", "https://novoasianfoodhall.com/pittsburgh-the-strip-district-novo-food-hall-about-page"),
        ],
    },
}


def render_guide(slug, guide, page_shell):
    title = guide["title"]
    sources = "business websites"
    if slug == "restaurants-in-strip-district":
        sources += ' and <a href="https://www.visitpittsburgh.com/neighborhoods/strip-district/strip-district-local-flavors/" style="text-decoration:underline">Visit Pittsburgh</a>'
    cards = []
    for name, address, label, detail, source in guide["places"]:
        cards.append(f'''    <article class="story-card">
      <span class="card-label">{escape(label)}</span>
      <h2 class="card-headline">{escape(name)}</h2>
      <p class="card-date">{escape(address)}, Pittsburgh</p>
      <p class="card-excerpt">{escape(detail)}</p>
      <a class="card-more" href="{escape(source, quote=True)}" rel="noopener">Official site for {escape(name)} &rarr;</a>
    </article>''')
    body = f'''  <div class="breadcrumb"><a href="/">Home</a><span>/</span><a href="/best/">Best Of</a><span>/</span><span>{escape(title)}</span></div>
  <div class="page-head">
    <span class="page-eyebrow">Best Of Pittsburgh</span>
    <h1 class="page-title">{escape(title)}</h1>
    <p class="page-deck">{escape(guide["deck"])}</p>
    <p class="page-count">Five verified places &bull; Updated September 22, 2026</p>
  </div>
  <main class="archive">
    <p class="page-deck" style="margin-bottom:28px">{escape(guide["intro"])}</p>
    <div class="card-grid">
{chr(10).join(cards)}
    </div>
    <p class="page-deck" style="margin-top:28px">Selection method: we checked locations and the stated reasons to visit against {sources} on September 22, 2026. These are editorial picks, with no paid placement or claim of a personal visit. <a href="/contact" style="text-decoration:underline">Send a correction</a> if a listing changes.</p>
  </main>'''
    canonical = f"https://www.thepittsburghwire.com/best/{slug}/"
    html = page_shell(f"{title} | The Pittsburgh Wire", guide["description"], canonical, body, active_nav="/best/")
    return html.replace('<meta name="robots" content="index, follow" />',
                        '<meta name="robots" content="index, follow" />\n  <meta name="wire:curated-guide" content="true" />', 1)


def write(repo, page_shell):
    for slug, guide in GUIDES.items():
        page = Path(repo) / "best" / slug / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(render_guide(slug, guide, page_shell), encoding="utf-8")
