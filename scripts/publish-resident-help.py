"""Publish the Pittsburgh resident help guides and connect them to the homepage."""
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_site import page_shell
from service_buying_guides import STYLE

SITE = "https://www.thepittsburghwire.com"
CITY = "https://www.pittsburghpa.gov/Resident-Services"
HELP = "/guides/pittsburgh-resident-faq/"
REQUEST = "/guides/pittsburgh-311-service-request/"
TRASH = "/guides/pittsburgh-trash-recycling-schedule/"
SNOW = "/guides/pittsburgh-snow-plow-map/"
RENT = "/guides/pittsburgh-rental-assistance/"

def link(url, text):
    return f'<a href="{escape(url, quote=True)}">{escape(text)}</a>'

def section(title, body):
    return f"<section><h2>{escape(title)}</h2>{body}</section>"

def write(route, title, deck, sections):
    breadcrumb = link("/", "Home")
    if route != HELP:
        breadcrumb += "<span>/</span>" + link(HELP, "Pittsburgh resident FAQ")
    body = f"""<div class="breadcrumb">{breadcrumb}</div>
<header class="page-head"><h1 class="page-title">{escape(title)}</h1><p class="page-deck">{escape(deck)}</p></header>
<main class="archive"><article class="service-guide">{''.join(sections)}
<p><small>Official sources checked November 28, 2026.</small></p></article></main>"""
    page = page_shell(escape(title + " | The Pittsburgh Wire"), escape(deck, quote=True), SITE + route, body)
    output = ROOT / route.strip("/") / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page.replace("</head>", STYLE + "</head>", 1), encoding="utf-8")

write(HELP, "Pittsburgh Resident FAQ and City Services",
      "Find your collection day, report a city service issue, or check which streets snow crews have treated.", [
    section("Who handles services at my address?", f"<p>Start with the street address. A Pittsburgh mailing address can fall outside City of Pittsburgh limits. Check the municipality before using the city’s collection calendar or service form. If you live in another borough or township, use its local office or hauler for instructions.</p><p>{link('/municipalities/', 'Find your Allegheny County municipality')} · {link(CITY, 'City of Pittsburgh resident services')}</p>"),
    section("Where can I ask for help with rent?", f"<p>ACTION-Housing screens renters for assistance by phone and email. {link(RENT, 'Find rental assistance and eviction prevention contacts')}.</p>"),
    section("Where do I report a pothole or broken streetlight?", f"<p>Use Pittsburgh 311 for non-emergency city concerns. A street address, cross street and clear description help staff identify the location. {link(REQUEST, 'How to file and track a 311 request')}.</p>"),
    section("When will my trash or recycling be picked up?", f"<p>Use your address to find your normal route, then check the city’s latest holiday or service notice. Trash and recycling can have different calendars. {link(TRASH, 'Find your collection day and report a missed pickup')}.</p>"),
    section("How can I follow proposed changes to city services?", f"<p>The city’s operating budget covers ongoing services. The capital plan lists projects such as street and park improvements. {link('/news/pittsburgh-2027-budget-hearing-december-10', 'Follow Pittsburgh’s 2027 budget hearing and scheduled vote')}.</p>"),
    section("Where can I see whether my street was plowed?", f"<p>The city publishes a vehicle dashboard and a route coverage map. Check both before drawing conclusions about a particular block. {link(SNOW, 'How to read Pittsburgh’s snow response maps')}.</p>"),
])
write(REQUEST, "How to File and Track a Pittsburgh 311 Request",
      "Use Pittsburgh 311 to report non-emergency city issues and keep the ticket number for follow-up.", [
    section("What can I report?", f"<p>Pittsburgh 311 handles city service questions and non-emergency concerns such as potholes, streetlights, missed collection, and snow or ice issues. Confirm the issue is inside the City of Pittsburgh. {link(CITY + '/311', 'See Pittsburgh 311’s service information')}.</p>"),
    section("What should I include?", "<p>Give the exact location and describe what needs attention. For a street issue, note the nearest cross street and which side of the road it is on. For a missed pickup, specify trash or recycling and give the service address and scheduled day. For a streetlight, add a pole identifier if you can read it safely.</p>"),
    section("How do I submit and track it?", f"<p>Dial 311 from within the city or use the official online reporting link. Provide a valid email address if you want an emailed ticket number. Save that number with the request date so you can follow up on the same issue.</p><p>{link(CITY + '/311/Contacting-311', 'Open the City of Pittsburgh’s 311 contact and reporting options')}.</p>"),
    section("Can I look up past reports?", f"<p>Check your own ticket through the city’s 311 channels. If you are researching patterns across multiple streets, use {link('/guides/read-pittsburgh-311-request-records/', 'the Wire’s guide to public 311 records')}.</p>"),
])
write(TRASH, "Pittsburgh Trash and Recycling Pickup Schedule",
      "Find your city collection day by address, check holiday delays and report a missed pickup.", [
    section("Find your collection day", f"<p>Open the Collection Map section of the city’s schedule page. Its address tools identify the refuse and recycling days for a specific property. If you use a printed calendar, first confirm whether your address is in the Northern and Southern group or the Central and Eastern group.</p><p>{link(CITY + '/Trash-Recycling/Collection-Schedule-and-Newsletter', 'Open the city’s collection schedule and address lookup')}.</p>"),
    section("2027 collection calendar update", f"<p>The city says its 2027 printed newsletter is delayed while it adjusts the program. Regular service days stay the same. The schedule page now lists January and February recycling weeks for both collection areas. Match the week to your area and the pickup day to your street address, and check the listed holiday exceptions before setting out bins.</p><p>{link(CITY + '/Trash-Recycling', 'Read the city’s newsletter delay notice')}.</p>"),
    section("Does a holiday change my pickup?", "<p>Check the date-specific city notice as well as your normal day. The collection schedule explains that an observed collection holiday falling on or before your usual day generally moves that week’s pickup back one day. Follow the city’s latest notice if it lists a different arrangement for that week.</p>"),
    section("Christmas week pickup in 2026", f"<p>Christmas Day falls on Friday, December 25. Under the city’s published one-day holiday rule, a regular Friday pickup shifts to Saturday, December 26. Earlier weekday routes are outside that shift. If recycling is due for your address that week, check its date in the city’s address lookup. Check again before setting bins out in case the city issues a newer service notice.</p><p>{link(CITY + '/Trash-Recycling/Collection-Schedule-and-Newsletter', 'Check Christmas week dates on the city’s collection calendar')}.</p>"),
    section("What if the truck skipped my pickup?", f"<p>Confirm the date, whether your material was eligible for curbside collection, and when it was set out. If it was a missed city pickup, report it with your address and the type of material. {link(REQUEST, 'File a Pittsburgh 311 request')}.</p>"),
    section("Can I put furniture or electronics out with the trash?", f"<p>Check the city’s bulk pickup instructions before setting out furniture or other large items. TVs and computers need a separate disposal route. {link(CITY + '/Trash-Recycling/Curbside-Pick-Up', 'Check curbside and bulk rules')} · {link(CITY + '/Trash-Recycling/Drop-Off-Info-Additional-Resources/Waste-Disposal-Resources', 'Find disposal options for excluded items')}.</p>"),
])
write(SNOW, "Pittsburgh Snow Plow Map and Street Treatment",
      "Find the city’s snow response maps, understand gaps in the coverage and report a street that still needs treatment.", [
    section("Which map should I use?", f"<p>The vehicle dashboard shows a selection of trucks and their route history. The city says locations are delayed and some treated routes are missing. For a block-level check, also open the separate Snow Route Coverage map on the same page. Its colored lines indicate where vehicles have traveled during treatment.</p><p>{link(CITY + '/Snow-Removal/Snow-Response-Updates', 'Open both city snow response maps')}.</p>"),
    section("Does a blank street mean it was skipped?", "<p>A blank line can reflect missing dashboard data. Check the coverage map and the timestamp, then compare nearby blocks. A route line records vehicle travel and cannot confirm the current condition of the road surface.</p>"),
    section("When can I report a street that still needs treatment?", f"<p>The city asks residents to wait until 24 hours after snowfall ends before reporting a street that still has not been plowed or salted. If you submit a request, include the street, cross streets and affected stretch. {link(CITY + '/Snow-Removal/Snow-Ice', 'Read the city’s snow and ice guidance')} · {link(REQUEST, 'File a Pittsburgh 311 request')}.</p>"),
])
write(RENT, "Pittsburgh Rental Assistance and Eviction Prevention",
      "Find the ACTION-Housing intake number, check city and county options, and gather documents for screening.", [
    section("Where should I start?", "<p>Call ACTION-Housing at <a href='tel:+14122480021'>412-248-0021</a> or email <a href='mailto:rentalassistance@actionhousing.org'>rentalassistance@actionhousing.org</a>. ACTION-Housing says its drop-in center closed June 30, 2026, and intake continues by phone and email. Ask which programs cover your address and what documentation they need. Assistance depends on eligibility and available funding.</p>"),
    section("What does the City of Pittsburgh program cover?", "<p>The URA’s Housing Stabilization Program lists up to $6,000 in short-term help for eligible renters within city limits. Its published income limit is 50% of area median income, and households can apply once every three years. Confirm your municipality by street address and ask the intake team which income limit applies to your household size.</p><p><a href='https://www.ura.org/pages/housing-stabilization-program'>Read the URA program requirements</a> · <a href='/municipalities/'>Check your municipality</a></p>"),
    section("What if I live elsewhere in Allegheny County?", "<p>The Allegheny Housing Stabilization Collaborative uses the same ACTION-Housing intake contacts and lists rental assistance, mediation and legal support. It applies its own screening criteria. Tell intake your municipality and whether you have a filed eviction case or a completed mediation agreement so the team can direct you to applicable services.</p><p><a href='https://actionhousing.org/our-services/allegheny-housing-stabilization-collaborative/'>Check the collaborative’s intake and eligibility information</a>.</p>"),
    section("What should I gather before screening?", "<p>Gather a signed lease, proof of income such as pay stubs or benefits letters, and any eviction notice, docket information or completed mediation agreement you have. Keep the intake reply and respond promptly if the provider asks for another document. Free interpretation is available through the city program’s screening process.</p>"),
])
routes = (HELP, REQUEST, TRASH, SNOW, RENT)
sitemap = ROOT / "sitemap.xml"
xml = sitemap.read_text(encoding="utf-8")
entries = ''.join(f"  <url><loc>{SITE}{route}</loc></url>\n" for route in routes if f"<loc>{SITE}{route}</loc>" not in xml)
sitemap.write_text(xml.replace("</urlset>", entries + "</urlset>", 1), encoding="utf-8")

home = ROOT / "index.html"
html = home.read_text(encoding="utf-8")
anchor = '<!-- buyer-intent-release:start -->'
if f'href="{HELP}"' not in html:
    assert anchor in html, "Homepage content insertion point missing"
    block = f'<section class="section" aria-labelledby="resident-help"><div class="wrap container prose"><h2 id="resident-help">Everyday Pittsburgh questions</h2><p>{link(HELP, "Resident FAQ")} · {link(REQUEST, "Report a city issue")} · {link(TRASH, "Find trash and recycling days")} · {link(SNOW, "Check snow plow routes")}</p></div></section>\n'
    home.write_text(html.replace(anchor, block + anchor, 1), encoding="utf-8")
