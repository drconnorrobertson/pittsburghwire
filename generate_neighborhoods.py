#!/usr/bin/env python3
"""
Pittsburgh Wire Neighborhood Landing Page Generator
Scans all articles and directory pages, maps them to neighborhoods,
and generates individual neighborhood pages + hub page.
"""

import os
import re
import html
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(BASE_DIR, "news")
DIR_DIR = os.path.join(BASE_DIR, "directory")
NEIGHBORHOODS_DIR = os.path.join(BASE_DIR, "neighborhoods")
SITE_URL = "https://www.thepittsburghwire.com"

# ─── Neighborhood definitions ───────────────────────────────────────────────

NEIGHBORHOODS = {
    "lawrenceville": {
        "name": "Lawrenceville",
        "slug": "lawrenceville",
        "description": [
            "Lawrenceville has become one of Pittsburgh's most dynamic neighborhoods, stretching along Butler Street from the 16th Street Bridge to Morningside. Once a blue-collar enclave known for its row houses and corner bars, the neighborhood has experienced a remarkable transformation over the past decade into a hub for independent restaurants, craft breweries, boutique shops, and creative studios.",
            "The neighborhood's three distinct sections -- Lower Lawrenceville, Central Lawrenceville, and Upper Lawrenceville -- each carry their own character. Lower Lawrenceville anchors the tech and startup scene, with companies like Aurora Innovation and numerous CMU spinouts choosing the area for their offices. Central Lawrenceville is the commercial heart, where Butler Street buzzes with foot traffic seven days a week. Upper Lawrenceville retains more of its residential, family-oriented feel while welcoming thoughtful new development.",
            "Despite rapid growth, Lawrenceville has maintained its identity through strong community organizations like the Lawrenceville Corporation and Lawrenceville United, which advocate for responsible development that serves longtime residents alongside newcomers. The result is a neighborhood that balances Pittsburgh's industrial heritage with a forward-looking creative energy."
        ],
        "keywords": ["Lawrenceville", "Butler Street", "Arsenal", "40th Street"],
        "nearby": ["strip-district", "bloomfield", "garfield", "polish-hill"],
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
        "image_alt": "Lawrenceville neighborhood streetscape in Pittsburgh"
    },
    "strip-district": {
        "name": "Strip District",
        "slug": "strip-district",
        "description": [
            "The Strip District is Pittsburgh's vibrant marketplace neighborhood, running along the Allegheny River from 11th Street to 33rd Street. For over a century, this half-mile stretch of Penn Avenue has been the city's wholesale food district, and it remains the place where Pittsburghers come to buy fresh produce, imported cheeses, handmade pasta, specialty meats, and just about anything else.",
            "In recent years, the Strip has evolved well beyond its roots as a wholesale market. Major tech companies have planted their flags here, with Duolingo expanding its headquarters and numerous startups filling renovated warehouse spaces. The neighborhood's mix of century-old produce vendors, trendy restaurants, and tech offices creates an energy unlike anywhere else in the city. On Saturday mornings, the streets overflow with shoppers navigating between Pennsylvania Macaroni Company, Klavon's Ice Cream, and dozens of street vendors.",
            "Development continues at a rapid pace, with new mixed-use projects adding residential units and modern office space while preserving the industrial character that makes the Strip unique. The neighborhood serves as a model for how Pittsburgh blends its working-class heritage with 21st-century innovation."
        ],
        "keywords": ["Strip District", "Penn Avenue", "Smallman Street", "Strip"],
        "nearby": ["lawrenceville", "downtown", "polish-hill", "bloomfield"],
        "image": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200&q=80",
        "image_alt": "Strip District market area in Pittsburgh"
    },
    "east-liberty": {
        "name": "East Liberty",
        "slug": "east-liberty",
        "description": [
            "East Liberty has emerged as one of Pittsburgh's most striking urban comeback stories. Once the city's most important commercial district outside of downtown, the neighborhood fell into decades of decline after a misguided 1960s urban renewal project severed its street grid. Today, East Liberty is thriving again, anchored by Google's Pittsburgh office, a booming restaurant scene, and significant residential development.",
            "The neighborhood's revival centers on Penn Avenue and Centre Avenue, where a mix of national retailers and independent businesses coexist in renovated storefronts and new construction. The Bakery Square development, built on the former Nabisco factory site, brought Google and other tech tenants to the area, sparking a wave of investment that has rippled through surrounding blocks. Coworking spaces, tech hubs, and startup incubators now dot the landscape.",
            "East Liberty's resurgence has not been without tension, as rising rents and displacement of longtime residents have prompted important conversations about equitable development. Community organizations and city leaders continue working to ensure the neighborhood's growth benefits everyone, making East Liberty a bellwether for how Pittsburgh navigates its broader economic transformation."
        ],
        "keywords": ["East Liberty", "East End", "Penn Circle", "Bakery Square"],
        "nearby": ["shadyside", "bloomfield", "garfield", "point-breeze"],
        "image": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1200&q=80",
        "image_alt": "East Liberty commercial district in Pittsburgh"
    },
    "bloomfield": {
        "name": "Bloomfield",
        "slug": "bloomfield",
        "description": [
            "Bloomfield, proudly known as Pittsburgh's \"Little Italy,\" has been the heart of the city's Italian-American community for over a century. Liberty Avenue, the neighborhood's main commercial corridor, is lined with Italian bakeries, red-sauce restaurants, specialty grocers, and family-owned businesses that have served the community for generations. The annual Little Italy Days festival draws tens of thousands of visitors each summer.",
            "While Bloomfield honors its Italian heritage, the neighborhood has also welcomed a new wave of independent businesses that reflect Pittsburgh's evolving identity. Craft cocktail bars sit alongside decades-old pizza shops, and contemporary art galleries share blocks with traditional barber shops. This blend of old and new gives Bloomfield a character that feels both rooted and alive, attracting young professionals and families alike.",
            "Bloomfield's residential streets are defined by tidy row houses, front porches, and a walkable scale that many newer developments try to replicate. The neighborhood's strong sense of community, anchored by institutions like the Bloomfield-Garfield Corporation and the Immaculate Conception Church, has helped it navigate growth while preserving the tight-knit feel that makes it one of Pittsburgh's most beloved places to live."
        ],
        "keywords": ["Bloomfield", "Little Italy", "Liberty Avenue", "Liberty Ave"],
        "nearby": ["lawrenceville", "garfield", "shadyside", "east-liberty"],
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
        "image_alt": "Bloomfield Liberty Avenue in Pittsburgh"
    },
    "hazelwood-green": {
        "name": "Hazelwood Green",
        "slug": "hazelwood-green",
        "description": [
            "Hazelwood Green represents one of the most ambitious urban redevelopment projects in the United States. This 178-acre site along the Monongahela River was once home to the Jones & Laughlin Steel Company's coke works, and its transformation into a mixed-use innovation district is a powerful symbol of Pittsburgh's post-industrial reinvention. The project is led by a partnership between the Richard King Mellon Foundation, the Heinz Endowments, and the Claude Worthington Benedum Foundation.",
            "The development plan calls for a walkable, transit-connected neighborhood with space for research labs, advanced manufacturing, offices, retail, and housing. Mill 19, the signature adaptive reuse of a historic steel mill building, now houses Carnegie Mellon University's Manufacturing Futures Initiative and the Advanced Robotics for Manufacturing Institute. New tenants continue to commit to the site, bringing biotech, climate tech, and workforce training operations.",
            "Hazelwood Green is designed from the ground up with sustainability in mind, incorporating green infrastructure, stormwater management, and a commitment to net-zero energy. The project also prioritizes inclusive development, with goals for affordable housing and local hiring that aim to benefit the surrounding Hazelwood community alongside the broader Pittsburgh region."
        ],
        "keywords": ["Hazelwood Green", "Hazelwood", "Mill 19", "Monongahela"],
        "nearby": ["south-side", "oakland", "squirrel-hill"],
        "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80",
        "image_alt": "Hazelwood Green development site along the Monongahela River"
    },
    "south-side": {
        "name": "South Side",
        "slug": "south-side",
        "description": [
            "Pittsburgh's South Side stretches along the southern bank of the Monongahela River, centered on East Carson Street, one of the longest commercial corridors in the country. Historically a neighborhood of steelworkers and Eastern European immigrants, the South Side retains much of its working-class character even as it has become one of the city's most popular entertainment and dining destinations.",
            "East Carson Street is home to an eclectic mix of bars, restaurants, vintage shops, tattoo parlors, and independent retailers that give the neighborhood its distinctive energy. The South Side Works development, built on the former LTV Steel site, has added modern office space, retail, and residential units to the neighborhood, attracting companies and young professionals. The area continues to evolve with new mixed-use projects in various stages of planning and construction.",
            "Beyond the commercial bustle, the South Side's residential streets climb the steep hillsides above Carson Street, offering some of the city's most dramatic views. The neighborhood's strong community fabric, diverse housing stock, and convenient location -- just across the river from downtown and Oakland -- make it one of Pittsburgh's most enduringly popular places to call home."
        ],
        "keywords": ["South Side", "South Side Works", "Carson Street", "East Carson", "SouthSide"],
        "nearby": ["downtown", "mt-washington", "hazelwood-green", "oakland"],
        "image": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200&q=80",
        "image_alt": "South Side neighborhood along the Monongahela River in Pittsburgh"
    },
    "downtown": {
        "name": "Downtown / Golden Triangle",
        "slug": "downtown",
        "description": [
            "Downtown Pittsburgh, known locally as the Golden Triangle, sits at the confluence of the Allegheny, Monongahela, and Ohio rivers at Point State Park. The city's central business district is compact and walkable, defined by a mix of historic architecture and modern towers that house the headquarters of major corporations including PNC Financial Services, PPG Industries, U.S. Steel, and Highmark Health.",
            "The Cultural District, anchored along Penn Avenue between the Allegheny River and Stanwix Street, is home to world-class performing arts venues including Heinz Hall, the Benedum Center, and the Byham Theater. The Pittsburgh Cultural Trust has invested hundreds of millions in transforming this area into one of the country's most vibrant arts districts, and the recent opening of Arts Landing has added a major new civic green space to the downtown waterfront.",
            "Downtown is experiencing a new chapter of growth as developers convert underutilized office buildings into residential units, bringing a 24/7 population to what was traditionally a 9-to-5 district. Market Square, recently modernized with a new glass trellis and expanded dining, serves as the neighborhood's central gathering place. With the 2026 NFL Draft coming to Pittsburgh, downtown is poised for its biggest national spotlight in years."
        ],
        "keywords": ["Downtown", "Golden Triangle", "Market Square", "Cultural District", "Point State Park", "PPG Place"],
        "nearby": ["strip-district", "north-side", "south-side", "mt-washington"],
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
        "image_alt": "Downtown Pittsburgh skyline at the Golden Triangle"
    },
    "shadyside": {
        "name": "Shadyside",
        "slug": "shadyside",
        "description": [
            "Shadyside is one of Pittsburgh's most established and affluent neighborhoods, known for its tree-lined streets, upscale shopping, and beautifully maintained Victorian and Edwardian homes. Walnut Street, the neighborhood's primary commercial corridor, offers a curated mix of national retailers, independent boutiques, fine dining restaurants, and specialty shops that draw visitors from across the region.",
            "The neighborhood's other major artery, Ellsworth Avenue, provides a more intimate, locally-focused shopping and dining experience with acclaimed restaurants, wine bars, and independent retailers. Shadyside's residential blocks are among the most desirable in the city, featuring grand single-family homes, well-kept apartment buildings, and an active real estate market driven by proximity to UPMC hospitals, Carnegie Mellon University, and the University of Pittsburgh.",
            "Shadyside's walkability, strong public transit connections, and concentration of amenities make it a perennial favorite for young professionals, medical residents, and families. The neighborhood manages to feel both cosmopolitan and residential, offering the conveniences of city living within a leafy, neighborhood-scale setting."
        ],
        "keywords": ["Shadyside", "Walnut Street", "Ellsworth Avenue"],
        "nearby": ["east-liberty", "squirrel-hill", "oakland", "point-breeze", "bloomfield"],
        "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80",
        "image_alt": "Shadyside neighborhood tree-lined streets in Pittsburgh"
    },
    "squirrel-hill": {
        "name": "Squirrel Hill",
        "slug": "squirrel-hill",
        "description": [
            "Squirrel Hill is one of Pittsburgh's most diverse and culturally rich neighborhoods, anchored by two bustling commercial districts along Forbes Avenue and Murray Avenue. Home to the city's largest Jewish community and a growing population of immigrants from Asia and Eastern Europe, Squirrel Hill's restaurants, shops, and cultural institutions reflect a remarkable range of traditions and cuisines.",
            "Forbes Avenue near the intersection with Murray serves as the neighborhood's commercial heart, with a dense mix of restaurants, bakeries, bookshops, and service businesses. Murray Avenue adds its own character with kosher delis, international grocers, and longtime family businesses. The neighborhood is also home to several of Pittsburgh's most popular parks, including Frick Park, one of the largest municipal parks in Pennsylvania.",
            "Squirrel Hill's strong community identity, excellent schools, walkable streets, and proximity to the University of Pittsburgh and Carnegie Mellon have made it one of the most stable and sought-after neighborhoods in the city for decades. It remains a place where longtime Pittsburgh families and newcomers alike find common ground."
        ],
        "keywords": ["Squirrel Hill", "Murray Avenue", "Forbes Avenue", "Frick Park"],
        "nearby": ["shadyside", "oakland", "point-breeze", "hazelwood-green"],
        "image": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1200&q=80",
        "image_alt": "Squirrel Hill commercial district in Pittsburgh"
    },
    "oakland": {
        "name": "Oakland",
        "slug": "oakland",
        "description": [
            "Oakland is Pittsburgh's academic and medical powerhouse, home to the University of Pittsburgh, Carnegie Mellon University, and the sprawling UPMC medical campus. As the city's second-largest employment center after downtown, Oakland generates billions in economic activity and serves as the launching pad for much of Pittsburgh's innovation economy, from robotics and AI to biotech and healthcare.",
            "The neighborhood's grand civic architecture -- including the Cathedral of Learning, Soldiers and Sailors Memorial Hall, the Carnegie Museum complex, and Phipps Conservatory -- gives Oakland a sense of scale and ambition that distinguishes it from Pittsburgh's more intimate neighborhoods. Schenley Park, designed by Edward Bigelow in the 1890s, provides 456 acres of green space at Oakland's doorstep.",
            "Beyond the institutions, Oakland supports a lively student-driven commercial scene along Forbes and Fifth Avenues, with restaurants, cafes, and shops catering to the thousands of students and medical professionals who fill the neighborhood daily. Major expansion projects by both UPMC and the universities continue to reshape the landscape, reinforcing Oakland's role as the engine of Pittsburgh's knowledge economy."
        ],
        "keywords": ["Oakland", "University of Pittsburgh", "Carnegie Mellon", "CMU", "Schenley"],
        "nearby": ["shadyside", "squirrel-hill", "south-side", "hazelwood-green"],
        "image": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1200&q=80",
        "image_alt": "Oakland neighborhood with university buildings in Pittsburgh"
    },
    "north-side": {
        "name": "North Side / North Shore",
        "slug": "north-side",
        "description": [
            "Pittsburgh's North Side encompasses a collection of historic neighborhoods on the north bank of the Allegheny River, anchored by the North Shore waterfront district that is home to Acrisure Stadium, PNC Park, and the Andy Warhol Museum. Once an independent city called Allegheny before its annexation in 1907, the North Side retains a distinct identity shaped by its grand Victorian architecture, diverse communities, and evolving cultural scene.",
            "The North Shore itself has become a dining and entertainment destination, with a growing cluster of restaurants, breweries, and event spaces along the riverfront. The Mexican War Streets and Allegheny West neighborhoods feature some of the finest Victorian-era homes in the region, attracting preservation-minded buyers and tourists alike. Federal Street has seen significant new investment, with mixed-use developments adding modern amenities to the historic streetscape.",
            "With the 2026 NFL Draft staging its main events on the North Shore, the neighborhood is preparing for a national spotlight. Major infrastructure improvements, new hospitality investments, and community-driven planning efforts are positioning the North Side for its next chapter of growth while honoring its rich architectural and cultural heritage."
        ],
        "keywords": ["North Side", "North Shore", "Allegheny", "Federal Street", "PNC Park", "Acrisure Stadium"],
        "nearby": ["downtown", "lawrenceville", "polish-hill"],
        "image": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200&q=80",
        "image_alt": "North Shore waterfront and stadiums in Pittsburgh"
    },
    "mt-washington": {
        "name": "Mt. Washington",
        "slug": "mt-washington",
        "description": [
            "Mt. Washington sits atop the bluffs overlooking Pittsburgh's Golden Triangle, offering what USA Today once called the most beautiful view in America. The neighborhood is accessible via two historic inclines -- the Monongahela Incline and the Duquesne Incline -- that have been carrying passengers up the steep hillside since the 1870s. Grandview Avenue, the street that runs along the cliff's edge, provides a panoramic vista of the downtown skyline and three rivers that is iconic to Pittsburgh.",
            "Beyond the viewpoints, Mt. Washington is a residential neighborhood with a mix of housing styles, from modest rowhouses to contemporary hillside homes with floor-to-ceiling windows designed to capture the view. The Grandview Avenue corridor has long been home to fine dining restaurants, and a new wave of boutique hotel proposals and hospitality investments signals growing confidence in the neighborhood's tourism potential.",
            "Mt. Washington's unique topography, stunning views, and proximity to downtown make it one of Pittsburgh's most distinctive neighborhoods. Community groups are working to balance new development with the preservation of affordable housing and the neighborhood's eclectic, residential character."
        ],
        "keywords": ["Mt. Washington", "Mount Washington", "Grandview", "Incline", "Duquesne Incline", "Monongahela Incline"],
        "nearby": ["south-side", "downtown"],
        "image": "https://images.unsplash.com/photo-1460472178825-e5240623afd5?w=1200&q=80",
        "image_alt": "View from Mt. Washington overlooking downtown Pittsburgh"
    },
    "point-breeze": {
        "name": "Point Breeze",
        "slug": "point-breeze",
        "description": [
            "Point Breeze is one of Pittsburgh's most distinguished residential neighborhoods, known for its stately homes, quiet tree-canopied streets, and deep roots in the city's industrial history. The neighborhood was once home to the mansions of Pittsburgh's wealthiest industrialists, including the Frick, Mellon, and Heinz families, and that legacy of affluence is still visible in the grand homes along Penn Avenue and Reynolds Street.",
            "Today, Point Breeze combines its historic grandeur with a welcoming, family-oriented atmosphere. The neighborhood's proximity to Frick Park -- one of the largest urban parks in Pennsylvania -- gives residents access to miles of trails, playgrounds, and green space. The commercial offerings along Penn Avenue and at the Regent Square border provide everyday conveniences alongside locally-owned restaurants and shops.",
            "Point Breeze remains one of the most stable and desirable neighborhoods in Pittsburgh, attracting families, professionals, and anyone seeking a quieter pace of life within easy reach of Oakland, Shadyside, and Squirrel Hill. Its combination of architectural beauty, natural amenities, and community pride makes it a cornerstone of Pittsburgh's East End."
        ],
        "keywords": ["Point Breeze", "Frick Park", "Reynolds Street"],
        "nearby": ["squirrel-hill", "shadyside", "east-liberty", "regent-square"],
        "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80",
        "image_alt": "Point Breeze residential neighborhood in Pittsburgh"
    },
    "garfield": {
        "name": "Garfield",
        "slug": "garfield",
        "description": [
            "Garfield is a neighborhood in transition, where grassroots arts organizations and community development efforts are driving a creative renaissance on Pittsburgh's East End. Penn Avenue through Garfield has become the city's most vibrant arts corridor, with galleries, studios, and creative businesses occupying formerly vacant storefronts. The monthly Unblurred gallery crawl draws hundreds of visitors and has become a signature Pittsburgh cultural event.",
            "The neighborhood's revitalization has been community-led, with organizations like the Bloomfield-Garfield Corporation and Garfield Community Farm playing central roles in shaping development that serves existing residents. New construction and renovation projects are bringing market-rate and affordable housing to the neighborhood, while the ongoing transformation of Penn Avenue continues to attract artists, makers, and entrepreneurs.",
            "Garfield's location between Lawrenceville, Bloomfield, and East Liberty positions it at the crossroads of several of Pittsburgh's hottest neighborhoods, and its relatively affordable real estate has made it a magnet for creative professionals and first-time homebuyers. The neighborhood's trajectory offers a model for community-centered development in Pittsburgh and beyond."
        ],
        "keywords": ["Garfield", "Unblurred", "Penn Avenue Arts"],
        "nearby": ["lawrenceville", "bloomfield", "east-liberty"],
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80",
        "image_alt": "Garfield arts district along Penn Avenue in Pittsburgh"
    },
    "polish-hill": {
        "name": "Polish Hill",
        "slug": "polish-hill",
        "description": [
            "Polish Hill is a small, tight-knit neighborhood perched on a hilltop between Lawrenceville, the Strip District, and the Bloomfield Bridge. Named for the Polish immigrants who settled there in the late 19th century, the neighborhood retains a quiet, village-like atmosphere that feels worlds away from the bustling commercial corridors just minutes in any direction. The Immaculate Heart of Mary Church, with its twin copper domes, remains the neighborhood's most prominent landmark.",
            "In recent years, Polish Hill has attracted artists, musicians, and young professionals drawn by affordable rents, unique housing stock, and the neighborhood's independent spirit. The Gooski's bar on Brereton Street has long been a beloved dive bar and live music venue, and a growing number of small creative businesses have begun to fill in along the neighborhood's compact commercial blocks.",
            "Polish Hill's hillside location provides dramatic views of the Strip District, Lawrenceville, and the downtown skyline. The neighborhood's small scale, strong community identity, and central location make it one of Pittsburgh's hidden gems -- a place where old Pittsburgh and new Pittsburgh coexist comfortably."
        ],
        "keywords": ["Polish Hill", "Brereton Street", "Immaculate Heart"],
        "nearby": ["lawrenceville", "strip-district", "bloomfield"],
        "image": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200&q=80",
        "image_alt": "Polish Hill neighborhood hilltop view in Pittsburgh"
    },
    "regent-square": {
        "name": "Regent Square",
        "slug": "regent-square",
        "description": [
            "Regent Square is a charming, walkable neighborhood straddling the border of the City of Pittsburgh and several adjacent municipalities. Centered on the intersection of Braddock Avenue and South Braddock Avenue, its compact commercial district features a beloved independent movie theater, local restaurants, a popular coffee shop, and a handful of specialty stores that give it a small-town feel within the city.",
            "The neighborhood's residential streets are lined with well-maintained Craftsman bungalows, Tudor-style homes, and brick colonials, many dating to the early 20th century. Frick Park's eastern entrance sits at Regent Square's doorstep, giving residents direct access to hundreds of acres of wooded trails and recreational facilities. The combination of architectural charm, green space, and walkable amenities makes Regent Square perennially popular with families and professionals.",
            "Regent Square's strong neighborhood identity is maintained by an active business association and engaged residents who organize seasonal events, a farmers' market, and community initiatives. Its position as a gateway between Pittsburgh's East End and the Mon Valley communities to the east gives it a unique character that blends urban convenience with suburban tranquility."
        ],
        "keywords": ["Regent Square", "Braddock Avenue", "Frick Park"],
        "nearby": ["squirrel-hill", "point-breeze", "east-liberty"],
        "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80",
        "image_alt": "Regent Square neighborhood in Pittsburgh"
    },
    "hill-district": {
        "name": "Hill District",
        "slug": "hill-district",
        "description": [
            "The Hill District holds a singular place in Pittsburgh's history and cultural identity. Once known as \"Little Harlem\" for its thriving jazz scene and vibrant African-American community, the neighborhood produced legends including August Wilson, whose ten-play Pittsburgh Cycle immortalized life on its streets. The Hill's Wylie Avenue corridor was one of the most important jazz destinations in America during the mid-20th century.",
            "After decades of disinvestment following the construction of the Civic Arena -- which displaced thousands of residents -- the Hill District is experiencing a genuine renaissance. New businesses are opening along Centre Avenue, community-driven development projects are moving forward, and the long-promised reinvestment from the arena site is finally materializing. The neighborhood's proximity to downtown and Oakland positions it for continued growth.",
            "The Hill District's revitalization is being guided by community voices who are determined to ensure that new development benefits longtime residents. Organizations like the Hill District Consensus Group and the Hill Community Development Corporation are shaping a vision that honors the neighborhood's extraordinary cultural legacy while building an economically vibrant future."
        ],
        "keywords": ["Hill District", "Centre Avenue", "Wylie Avenue", "Crawford Grill"],
        "nearby": ["downtown", "oakland", "polish-hill"],
        "image": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1200&q=80",
        "image_alt": "Hill District neighborhood in Pittsburgh"
    },
    "homestead": {
        "name": "Homestead",
        "slug": "homestead",
        "description": [
            "Homestead is a borough along the Monongahela River that occupies a pivotal place in American labor and industrial history. The Homestead Strike of 1892, one of the most significant events in U.S. labor history, took place at the Carnegie Steel works that once dominated the riverfront. Today, that same site has been transformed into The Waterfront, a major retail and entertainment development that draws visitors from across the region.",
            "The Waterfront development brought new life to the former steel mill site with shops, restaurants, a movie theater, and residential units, but Homestead's story extends well beyond that one project. The borough's Eighth Avenue commercial district has seen new investment in recent years, with restaurants, breweries, and arts organizations setting up in renovated storefronts. The historic Homestead Grays Bridge and the Rivers of Steel National Heritage Area help tell the story of the community's industrial past.",
            "New residential development continues along the riverfront, adding modern apartments and condos to a community that offers relative affordability compared to city neighborhoods across the river. Homestead's combination of rich history, ongoing development, and river access makes it an increasingly attractive option for people looking for value and character in the greater Pittsburgh area."
        ],
        "keywords": ["Homestead", "Waterfront", "Eighth Avenue", "Rivers of Steel"],
        "nearby": ["hazelwood-green", "squirrel-hill", "south-side"],
        "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80",
        "image_alt": "Homestead waterfront development along the Monongahela River"
    },
}


# ─── Scanning functions ─────────────────────────────────────────────────────

def scan_articles():
    """Scan all news articles and extract title, date, slug, and full text for neighborhood matching."""
    articles = []
    if not os.path.isdir(NEWS_DIR):
        return articles
    for slug in sorted(os.listdir(NEWS_DIR)):
        idx = os.path.join(NEWS_DIR, slug, "index.html")
        if not os.path.isfile(idx):
            continue
        with open(idx, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract title
        m = re.search(r"<title>([^<]+)</title>", content)
        title = m.group(1).replace(" | The Pittsburgh Wire", "").strip() if m else slug
        # Extract date
        m = re.search(r'datePublished["\s:]+(\d{4}-\d{2}-\d{2})', content)
        if not m:
            m = re.search(r'article:published_time["\s]+content="(\d{4}-\d{2}-\d{2})', content)
        date = m.group(1) if m else "2026-01-01"
        # Extract section
        m = re.search(r'article-section-label">([^<]+)<', content)
        section = m.group(1).strip() if m else "News"
        # Extract description
        m = re.search(r'<meta name="description" content="([^"]+)"', content)
        desc = m.group(1).strip() if m else ""

        # Extract article body text (between article-body tags), stripping HTML
        body_text = ""
        body_match = re.search(r'class="article-body">(.*?)</article>', content, re.DOTALL)
        if body_match:
            body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))

        articles.append({
            "slug": slug,
            "title": title,
            "date": date,
            "section": section,
            "description": desc,
            "body_text": body_text,
            "content": content,
            "url": f"/news/{slug}"
        })
    return articles


def scan_directory():
    """Scan all directory business pages and extract name, neighborhood, slug, etc."""
    businesses = []
    if not os.path.isdir(DIR_DIR):
        return businesses
    for slug in sorted(os.listdir(DIR_DIR)):
        if slug == "index.html":
            continue
        idx = os.path.join(DIR_DIR, slug, "index.html")
        if not os.path.isfile(idx):
            continue
        with open(idx, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract name
        m = re.search(r"<title>([^|<]+)", content)
        name = m.group(1).strip() if m else slug
        # Extract neighborhood from info-value after Neighborhood label
        m = re.search(r'Neighborhood</span>\s*<span[^>]*>([^<]+)<', content)
        neighborhood = html.unescape(m.group(1).strip()) if m else ""
        # Extract category
        m = re.search(r'class="biz-cat-badge[^"]*"[^>]*>([^<]+)<', content)
        if not m:
            m = re.search(r'info-label">Category</span>\s*<span[^>]*>([^<]+)<', content)
        category = m.group(1).strip() if m else ""
        # Extract owner
        m = re.search(r'class="biz-owner[^"]*"[^>]*>([^<]+)<', content)
        if not m:
            m = re.search(r'info-label">(?:Founder|Owner|CEO)</span>\s*<span[^>]*>([^<]+)<', content)
        owner = m.group(1).strip() if m else ""
        # Extract description
        m = re.search(r'<meta name="description" content="([^"]+)"', content)
        desc = m.group(1).strip() if m else ""

        businesses.append({
            "slug": slug,
            "name": name,
            "neighborhood": neighborhood,
            "category": category,
            "owner": owner,
            "description": desc,
            "content": content,
            "url": f"/directory/{slug}"
        })
    return businesses


def match_neighborhood(text, keywords):
    """Check if any keyword appears in the text (case-insensitive)."""
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def map_content_to_neighborhoods(articles, businesses):
    """Map articles and businesses to each neighborhood."""
    mapping = {}
    for nid, ndata in NEIGHBORHOODS.items():
        mapping[nid] = {"articles": [], "businesses": []}
        kws = ndata["keywords"]
        for a in articles:
            # Match on title, description, slug, and article body text (not nav/footer)
            searchable = a["title"] + " " + a["description"] + " " + a["slug"] + " " + a.get("body_text", "")
            if match_neighborhood(searchable, kws):
                mapping[nid]["articles"].append(a)
        for b in businesses:
            # For businesses, only match on the explicit neighborhood field and description
            # NOT the full HTML content (which contains nav/footer with all neighborhood names)
            if any(kw.lower() in b["neighborhood"].lower() for kw in kws):
                mapping[nid]["businesses"].append(b)
            elif match_neighborhood(b["description"], kws):
                mapping[nid]["businesses"].append(b)
        # Sort articles by date descending
        mapping[nid]["articles"].sort(key=lambda x: x["date"], reverse=True)
    return mapping


# ─── HTML generation ─────────────────────────────────────────────────────────

def format_date_display(date_str):
    """Convert 2026-04-15 to April 15, 2026."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y").replace(" 0", " ")
    except:
        return date_str


def generate_neighborhood_page(nid, ndata, content_map):
    """Generate a single neighborhood landing page HTML."""
    name = ndata["name"]
    slug = ndata["slug"]
    description = ndata["description"]
    articles = content_map[nid]["articles"]
    businesses = content_map[nid]["businesses"]
    nearby = ndata["nearby"]
    image = ndata["image"]
    image_alt = ndata["image_alt"]

    meta_desc = description[0][:155].rsplit(" ", 1)[0] + "..."

    # Build articles HTML
    articles_html = ""
    if articles:
        for a in articles:
            articles_html += f'''
        <a href="{a["url"]}" class="article-card">
          <div class="article-card-section">{html.escape(a["section"])}</div>
          <div class="article-card-title">{html.escape(a["title"])}</div>
          <div class="article-card-desc">{html.escape(a["description"][:140])}</div>
          <div class="article-card-date">{format_date_display(a["date"])}</div>
        </a>'''
    else:
        articles_html = '<p class="empty-state">No articles yet. Check back soon for coverage of this neighborhood.</p>'

    # Build businesses HTML
    businesses_html = ""
    if businesses:
        for b in businesses:
            businesses_html += f'''
        <a href="{b["url"]}" class="biz-card">
          <div class="biz-card-top">
            <div class="biz-icon">&#9670;</div>
            <div class="biz-cat-badge">{html.escape(b["category"])}</div>
          </div>
          <div class="biz-name">{html.escape(b["name"])}</div>
          {f'<div class="biz-owner">{html.escape(b["owner"])}</div>' if b["owner"] else ""}
          <div class="biz-desc">{html.escape(b["description"][:120])}</div>
        </a>'''
    else:
        businesses_html = '<p class="empty-state">No directory businesses listed yet. Know a great business here? <a href="/about" style="color:var(--gold)">Let us know</a>.</p>'

    # Build nearby neighborhoods HTML
    nearby_html = ""
    for ns in nearby:
        if ns in NEIGHBORHOODS:
            nearby_html += f'<a href="/neighborhoods/{ns}" class="nearby-link">{NEIGHBORHOODS[ns]["name"]}</a>'

    # Description paragraphs
    desc_html = "\n".join(f"        <p>{d}</p>" for d in description)

    # Schema.org Place structured data
    schema = f'''{{
    "@context": "https://schema.org",
    "@type": "Place",
    "name": "{name}",
    "description": "{html.escape(description[0][:200])}",
    "address": {{
      "@type": "PostalAddress",
      "addressLocality": "Pittsburgh",
      "addressRegion": "PA",
      "addressCountry": "US"
    }},
    "url": "{SITE_URL}/neighborhoods/{slug}",
    "containedInPlace": {{
      "@type": "City",
      "name": "Pittsburgh",
      "sameAs": "https://en.wikipedia.org/wiki/Pittsburgh"
    }}
  }}'''

    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} | Pittsburgh Neighborhoods | The Pittsburgh Wire</title>
  <meta name="description" content="{html.escape(meta_desc)}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{SITE_URL}/neighborhoods/{slug}" />
  <meta property="og:title" content="{name} | Pittsburgh Neighborhoods" />
  <meta property="og:description" content="{html.escape(meta_desc)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{SITE_URL}/neighborhoods/{slug}" />
  <meta property="og:image" content="{image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{name} | Pittsburgh Neighborhoods" />
  <meta name="twitter:description" content="{html.escape(meta_desc)}" />
  <meta name="twitter:image" content="{image}" />
  <script type="application/ld+json">
  {schema}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&family=Barlow:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --black: #0d0d0d;
      --steel: #1c1c1e;
      --rust: #c0392b;
      --gold: #e8a020;
      --concrete: #2e2e2e;
      --smoke: #888;
      --light: #f0ece4;
      --off-white: #e8e4dc;
      --border: #333;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--black);
      color: var(--light);
      font-family: 'Barlow', sans-serif;
      font-size: 16px;
      line-height: 1.6;
      overflow-x: hidden;
    }}
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
      pointer-events: none;
      z-index: 9999;
      opacity: 0.35;
    }}
    a {{ color: inherit; text-decoration: none; }}

    /* MASTHEAD */
    .masthead {{
      background: var(--steel);
      border-bottom: 3px solid var(--rust);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .masthead-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      align-items: stretch;
      justify-content: space-between;
    }}
    .masthead-brand {{
      display: flex;
      flex-direction: column;
      padding: 14px 28px;
      border-right: 2px solid var(--border);
      text-decoration: none;
    }}
    .masthead-wire {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 11px;
      letter-spacing: 4px;
      color: var(--smoke);
      text-transform: uppercase;
    }}
    .masthead-title {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 28px;
      color: var(--gold);
      letter-spacing: 2px;
      line-height: 1;
    }}
    .masthead-nav {{
      display: flex;
      align-items: center;
    }}
    .masthead-nav a {{
      display: flex;
      align-items: center;
      padding: 0 22px;
      height: 100%;
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--smoke);
      border-right: 1px solid var(--border);
      transition: color 0.15s, background 0.15s;
    }}
    .masthead-nav a:hover {{ color: var(--gold); background: rgba(232,160,32,0.06); }}
    .masthead-nav a.active {{ color: var(--gold); }}

    /* HERO */
    .hero {{
      position: relative;
      height: 420px;
      overflow: hidden;
    }}
    .hero-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      filter: brightness(0.45);
    }}
    .hero-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(to top, rgba(13,13,13,0.95) 0%, rgba(13,13,13,0.3) 60%, rgba(13,13,13,0.5) 100%);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 48px 28px;
    }}
    .hero-inner {{
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }}
    .hero-eyebrow {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 4px;
      text-transform: uppercase;
      color: var(--rust);
      margin-bottom: 12px;
    }}
    .hero-headline {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(48px, 7vw, 96px);
      line-height: 0.9;
      letter-spacing: 1px;
      color: var(--light);
    }}
    .hero-sub {{
      margin-top: 16px;
      font-size: 15px;
      color: var(--smoke);
      max-width: 600px;
      line-height: 1.7;
    }}
    .hero-stats {{
      display: flex;
      gap: 36px;
      margin-top: 24px;
    }}
    .stat-num {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 36px;
      color: var(--gold);
      line-height: 1;
    }}
    .stat-label {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--smoke);
    }}

    /* BREADCRUMB */
    .breadcrumb {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 16px 28px;
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--smoke);
      display: flex;
      gap: 10px;
      align-items: center;
      border-bottom: 1px solid var(--border);
    }}
    .breadcrumb a {{ color: var(--smoke); transition: color 0.15s; }}
    .breadcrumb a:hover {{ color: var(--gold); }}
    .breadcrumb .sep {{ color: #444; }}

    /* CONTENT */
    .content {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 0 28px;
    }}

    /* ABOUT SECTION */
    .about-section {{
      padding: 60px 0;
      border-bottom: 1px solid var(--border);
    }}
    .about-section p {{
      font-size: 16px;
      line-height: 1.85;
      color: #bbb;
      margin-bottom: 20px;
      max-width: 800px;
    }}
    .about-section p:last-child {{ margin-bottom: 0; }}

    /* SECTION HEADERS */
    .section-label {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 36px;
      padding-top: 60px;
    }}
    .section-label-text {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 32px;
      letter-spacing: 2px;
      color: var(--light);
      white-space: nowrap;
    }}
    .section-label-line {{
      flex: 1;
      height: 1px;
      background: var(--border);
    }}
    .section-label-count {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--gold);
      border: 1px solid var(--gold);
      padding: 4px 12px;
      white-space: nowrap;
    }}

    /* ARTICLE CARDS */
    .article-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 2px;
      margin-bottom: 60px;
    }}
    .article-card {{
      background: var(--steel);
      border: 1px solid var(--border);
      padding: 28px 32px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: background 0.15s, border-color 0.15s;
      position: relative;
      overflow: hidden;
    }}
    .article-card::after {{
      content: '';
      position: absolute;
      left: 0; top: 0;
      width: 3px; height: 0;
      background: var(--rust);
      transition: height 0.2s ease;
    }}
    .article-card:hover {{ background: #222; border-color: #444; }}
    .article-card:hover::after {{ height: 100%; }}
    .article-card-section {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--rust);
    }}
    .article-card-title {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 24px;
      line-height: 1.05;
      color: var(--light);
    }}
    .article-card-desc {{
      font-size: 13px;
      color: var(--smoke);
      line-height: 1.6;
    }}
    .article-card-date {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 1px;
      color: #555;
      text-transform: uppercase;
    }}

    /* BIZ CARDS */
    .biz-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 2px;
      margin-bottom: 60px;
    }}
    .biz-card {{
      background: var(--steel);
      border: 1px solid var(--border);
      padding: 28px 32px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      transition: background 0.15s, border-color 0.15s;
      position: relative;
      overflow: hidden;
    }}
    .biz-card::after {{
      content: '';
      position: absolute;
      left: 0; top: 0;
      width: 3px; height: 0;
      background: var(--gold);
      transition: height 0.2s ease;
    }}
    .biz-card:hover {{ background: #222; border-color: #444; }}
    .biz-card:hover::after {{ height: 100%; }}
    .biz-card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .biz-icon {{
      width: 44px;
      height: 44px;
      background: var(--black);
      border: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      color: var(--gold);
    }}
    .biz-cat-badge {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--smoke);
      border: 1px solid var(--border);
      padding: 3px 10px;
    }}
    .biz-name {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 28px;
      line-height: 1;
      color: var(--light);
    }}
    .biz-owner {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 13px;
      font-weight: 600;
      color: var(--gold);
    }}
    .biz-desc {{
      font-size: 13px;
      color: var(--smoke);
      line-height: 1.7;
    }}

    /* NEARBY */
    .nearby-section {{
      padding: 60px 0;
      border-top: 1px solid var(--border);
    }}
    .nearby-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .nearby-link {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 12px 24px;
      border: 1px solid var(--border);
      color: var(--smoke);
      transition: all 0.15s;
    }}
    .nearby-link:hover {{
      border-color: var(--gold);
      color: var(--gold);
      background: rgba(232,160,32,0.06);
    }}

    /* EMPTY STATE */
    .empty-state {{
      color: var(--smoke);
      font-style: italic;
      padding: 40px 0;
    }}

    /* CTA */
    .cta-bar {{
      background: var(--steel);
      border-top: 3px solid var(--gold);
      padding: 48px 28px;
      text-align: center;
    }}
    .cta-bar h3 {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 36px;
      color: var(--light);
      margin-bottom: 12px;
    }}
    .cta-bar p {{
      color: var(--smoke);
      margin-bottom: 24px;
      max-width: 500px;
      margin-left: auto;
      margin-right: auto;
    }}
    .cta-links {{
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .cta-btn {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 12px 28px;
      transition: all 0.15s;
    }}
    .cta-btn-primary {{ background: var(--rust); color: #fff; }}
    .cta-btn-primary:hover {{ background: #a93226; }}
    .cta-btn-secondary {{ border: 1px solid var(--border); color: var(--smoke); }}
    .cta-btn-secondary:hover {{ border-color: var(--gold); color: var(--gold); }}

    /* FOOTER */
    .footer {{
      background: var(--steel);
      border-top: 1px solid var(--border);
      padding: 48px 28px 28px;
    }}
    .footer-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 48px;
    }}
    .footer-brand {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 24px;
      color: var(--gold);
      margin-bottom: 8px;
    }}
    .footer-tagline {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #555;
      margin-bottom: 16px;
    }}
    .footer-copy {{
      font-size: 12px;
      color: #444;
    }}
    .footer-heading {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--smoke);
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }}
    .footer-links {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .footer-links a {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 13px;
      color: #666;
      letter-spacing: 1px;
      transition: color 0.15s;
    }}
    .footer-links a:hover {{ color: var(--gold); }}

    @media (max-width: 900px) {{
      .masthead-nav {{ display: none; }}
      .hero {{ height: 320px; }}
      .hero-headline {{ font-size: 42px; }}
      .article-grid, .biz-grid {{ grid-template-columns: 1fr; }}
      .hero-stats {{ flex-wrap: wrap; gap: 20px; }}
      .footer-inner {{ grid-template-columns: 1fr; gap: 32px; }}
    }}
  </style>
</head>
<body>
  <header class="masthead">
    <div class="masthead-inner">
      <a href="/" class="masthead-brand">
        <span class="masthead-wire">The Pittsburgh Wire</span>
        <span class="masthead-title">Neighborhoods</span>
      </a>
      <nav class="masthead-nav">
        <a href="/">Home</a>
        <a href="/neighborhoods" class="active">Neighborhoods</a>
        <a href="/directory">Directory</a>
        <a href="/about">About</a>
      </nav>
    </div>
  </header>

  <div class="hero">
    <img class="hero-img" src="{image}" alt="{html.escape(image_alt)}" />
    <div class="hero-overlay">
      <div class="hero-inner">
        <div class="hero-eyebrow">Pittsburgh Neighborhood</div>
        <h1 class="hero-headline">{name}</h1>
        <p class="hero-sub">{html.escape(description[0][:180]).rsplit(" ", 1)[0]}...</p>
        <div class="hero-stats">
          <div>
            <span class="stat-num">{len(articles)}</span>
            <span class="stat-label">Article{"s" if len(articles) != 1 else ""}</span>
          </div>
          <div>
            <span class="stat-num">{len(businesses)}</span>
            <span class="stat-label">Business{"es" if len(businesses) != 1 else ""}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="breadcrumb">
    <a href="/">Home</a>
    <span class="sep">/</span>
    <a href="/neighborhoods">Neighborhoods</a>
    <span class="sep">/</span>
    <span style="color:var(--light)">{name}</span>
  </div>

  <div class="content">
    <div class="about-section">
{desc_html}
    </div>

    <div class="section-label">
      <span class="section-label-text">Latest from {name}</span>
      <span class="section-label-line"></span>
      <span class="section-label-count">{len(articles)} Article{"s" if len(articles) != 1 else ""}</span>
    </div>
    <div class="article-grid">
{articles_html}
    </div>

    <div class="section-label">
      <span class="section-label-text">Businesses in {name}</span>
      <span class="section-label-line"></span>
      <span class="section-label-count">{len(businesses)} Business{"es" if len(businesses) != 1 else ""}</span>
    </div>
    <div class="biz-grid">
{businesses_html}
    </div>

    <div class="nearby-section">
      <div class="section-label" style="padding-top:0">
        <span class="section-label-text">Nearby Neighborhoods</span>
        <span class="section-label-line"></span>
      </div>
      <div class="nearby-grid">
{nearby_html}
      </div>
    </div>
  </div>

  <div class="cta-bar">
    <h3>Explore More of Pittsburgh</h3>
    <p>Discover the businesses, people, and stories shaping every corner of the Steel City.</p>
    <div class="cta-links">
      <a href="/neighborhoods" class="cta-btn cta-btn-primary">All Neighborhoods</a>
      <a href="/directory" class="cta-btn cta-btn-secondary">Business Directory</a>
      <a href="/" class="cta-btn cta-btn-secondary">Latest News</a>
    </div>
  </div>

  <footer class="footer">
    <div class="footer-inner">
      <div>
        <div class="footer-brand">The Pittsburgh Wire</div>
        <p class="footer-tagline">Good News, Only. Always Forward.</p>
        <p class="footer-copy">&copy; 2026 The Pittsburgh Wire. All rights reserved.</p>
      </div>
      <div>
        <div class="footer-heading">Sections</div>
        <ul class="footer-links">
          <li><a href="/">Home</a></li>
          <li><a href="/neighborhoods">Neighborhoods</a></li>
          <li><a href="/directory">Business Directory</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-heading">Popular Neighborhoods</div>
        <ul class="footer-links">
          <li><a href="/neighborhoods/lawrenceville">Lawrenceville</a></li>
          <li><a href="/neighborhoods/strip-district">Strip District</a></li>
          <li><a href="/neighborhoods/east-liberty">East Liberty</a></li>
          <li><a href="/neighborhoods/oakland">Oakland</a></li>
          <li><a href="/neighborhoods/downtown">Downtown</a></li>
          <li><a href="/neighborhoods/shadyside">Shadyside</a></li>
        </ul>
      </div>
    </div>
  </footer>
</body>
</html>'''
    return page_html


def generate_hub_page(content_map):
    """Generate the main /neighborhoods/index.html hub page."""
    # Sort neighborhoods alphabetically
    sorted_hoods = sorted(NEIGHBORHOODS.items(), key=lambda x: x[1]["name"])

    cards_html = ""
    for nid, ndata in sorted_hoods:
        n_articles = len(content_map[nid]["articles"])
        n_biz = len(content_map[nid]["businesses"])
        short_desc = ndata["description"][0][:140].rsplit(" ", 1)[0] + "..."
        cards_html += f'''
      <a href="/neighborhoods/{ndata["slug"]}" class="hood-card">
        <div class="hood-card-img-wrap">
          <img class="hood-card-img" src="{ndata["image"]}" alt="{html.escape(ndata["image_alt"])}" />
        </div>
        <div class="hood-card-body">
          <div class="hood-card-name">{ndata["name"]}</div>
          <div class="hood-card-desc">{html.escape(short_desc)}</div>
          <div class="hood-card-stats">
            <span>{n_articles} article{"s" if n_articles != 1 else ""}</span>
            <span class="hood-stat-sep">&bull;</span>
            <span>{n_biz} business{"es" if n_biz != 1 else ""}</span>
          </div>
        </div>
      </a>'''

    total_articles = sum(len(content_map[nid]["articles"]) for nid in NEIGHBORHOODS)
    total_biz = sum(len(content_map[nid]["businesses"]) for nid in NEIGHBORHOODS)

    hub_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Pittsburgh Neighborhoods | The Pittsburgh Wire</title>
  <meta name="description" content="Explore Pittsburgh's neighborhoods. Local news, businesses, and stories from Lawrenceville, Strip District, Oakland, Shadyside, and more." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{SITE_URL}/neighborhoods" />
  <meta property="og:title" content="Pittsburgh Neighborhoods | The Pittsburgh Wire" />
  <meta property="og:description" content="Explore Pittsburgh's neighborhoods. Local news, businesses, and stories from every corner of the Steel City." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{SITE_URL}/neighborhoods" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Pittsburgh Neighborhoods | The Pittsburgh Wire" />
  <meta name="twitter:description" content="Explore Pittsburgh's neighborhoods. Local news, businesses, and stories from every corner of the Steel City." />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Pittsburgh Neighborhoods",
    "description": "Explore Pittsburgh's neighborhoods. Local news, businesses, and stories from every corner of the Steel City.",
    "url": "{SITE_URL}/neighborhoods",
    "publisher": {{
      "@type": "Organization",
      "name": "The Pittsburgh Wire",
      "url": "{SITE_URL}"
    }}
  }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&family=Barlow:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --black: #0d0d0d;
      --steel: #1c1c1e;
      --rust: #c0392b;
      --gold: #e8a020;
      --concrete: #2e2e2e;
      --smoke: #888;
      --light: #f0ece4;
      --off-white: #e8e4dc;
      --border: #333;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--black);
      color: var(--light);
      font-family: 'Barlow', sans-serif;
      font-size: 16px;
      line-height: 1.6;
      overflow-x: hidden;
    }}
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
      pointer-events: none;
      z-index: 9999;
      opacity: 0.35;
    }}
    a {{ color: inherit; text-decoration: none; }}

    .masthead {{
      background: var(--steel);
      border-bottom: 3px solid var(--rust);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .masthead-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      align-items: stretch;
      justify-content: space-between;
    }}
    .masthead-brand {{
      display: flex;
      flex-direction: column;
      padding: 14px 28px;
      border-right: 2px solid var(--border);
      text-decoration: none;
    }}
    .masthead-wire {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 11px;
      letter-spacing: 4px;
      color: var(--smoke);
      text-transform: uppercase;
    }}
    .masthead-title {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 28px;
      color: var(--gold);
      letter-spacing: 2px;
      line-height: 1;
    }}
    .masthead-nav {{
      display: flex;
      align-items: center;
    }}
    .masthead-nav a {{
      display: flex;
      align-items: center;
      padding: 0 22px;
      height: 100%;
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--smoke);
      border-right: 1px solid var(--border);
      transition: color 0.15s, background 0.15s;
    }}
    .masthead-nav a:hover {{ color: var(--gold); background: rgba(232,160,32,0.06); }}
    .masthead-nav a.active {{ color: var(--gold); }}

    .hero {{
      background: var(--steel);
      border-bottom: 1px solid var(--border);
      padding: 72px 28px 60px;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: 'NEIGHBORHOODS';
      position: absolute;
      bottom: -20px;
      right: -20px;
      font-family: 'Bebas Neue', sans-serif;
      font-size: 160px;
      color: rgba(255,255,255,0.02);
      letter-spacing: -5px;
      pointer-events: none;
      line-height: 1;
    }}
    .hero-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 40px;
      align-items: end;
    }}
    .hero-eyebrow {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 4px;
      text-transform: uppercase;
      color: var(--rust);
      margin-bottom: 16px;
    }}
    .hero-headline {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(56px, 8vw, 110px);
      line-height: 0.9;
      letter-spacing: 1px;
      color: var(--light);
    }}
    .hero-headline span {{ color: var(--gold); display: block; }}
    .hero-sub {{
      margin-top: 24px;
      font-size: 16px;
      color: var(--smoke);
      max-width: 520px;
      line-height: 1.7;
    }}
    .hero-stats {{
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding: 28px 32px;
      background: var(--black);
      border: 1px solid var(--border);
      border-top: 3px solid var(--gold);
      min-width: 180px;
    }}
    .stat {{ text-align: center; }}
    .stat-num {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 48px;
      color: var(--gold);
      line-height: 1;
      display: block;
    }}
    .stat-label {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--smoke);
    }}
    .stat-divider {{ height: 1px; background: var(--border); }}

    .breadcrumb {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 16px 28px;
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--smoke);
      display: flex;
      gap: 10px;
      align-items: center;
      border-bottom: 1px solid var(--border);
    }}
    .breadcrumb a {{ color: var(--smoke); transition: color 0.15s; }}
    .breadcrumb a:hover {{ color: var(--gold); }}
    .breadcrumb .sep {{ color: #444; }}

    .content {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 48px 28px 80px;
    }}

    .hood-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 2px;
    }}
    .hood-card {{
      background: var(--steel);
      border: 1px solid var(--border);
      overflow: hidden;
      transition: background 0.15s, border-color 0.15s, transform 0.2s;
      display: flex;
      flex-direction: column;
    }}
    .hood-card:hover {{ background: #222; border-color: #444; transform: translateY(-2px); }}
    .hood-card-img-wrap {{
      height: 180px;
      overflow: hidden;
      position: relative;
    }}
    .hood-card-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      filter: brightness(0.6);
      transition: filter 0.3s, transform 0.3s;
    }}
    .hood-card:hover .hood-card-img {{ filter: brightness(0.75); transform: scale(1.03); }}
    .hood-card-body {{
      padding: 24px 28px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      flex: 1;
    }}
    .hood-card-name {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 32px;
      line-height: 1;
      color: var(--light);
    }}
    .hood-card-desc {{
      font-size: 13px;
      color: var(--smoke);
      line-height: 1.7;
      flex: 1;
    }}
    .hood-card-stats {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 12px;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: var(--gold);
      padding-top: 12px;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 8px;
    }}
    .hood-stat-sep {{ color: #444; }}

    .footer {{
      background: var(--steel);
      border-top: 1px solid var(--border);
      padding: 48px 28px 28px;
    }}
    .footer-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 48px;
    }}
    .footer-brand {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 24px;
      color: var(--gold);
      margin-bottom: 8px;
    }}
    .footer-tagline {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #555;
      margin-bottom: 16px;
    }}
    .footer-copy {{
      font-size: 12px;
      color: #444;
    }}
    .footer-heading {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--smoke);
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }}
    .footer-links {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .footer-links a {{
      font-family: 'Barlow Condensed', sans-serif;
      font-size: 13px;
      color: #666;
      letter-spacing: 1px;
      transition: color 0.15s;
    }}
    .footer-links a:hover {{ color: var(--gold); }}

    @media (max-width: 900px) {{
      .masthead-nav {{ display: none; }}
      .hero-inner {{ grid-template-columns: 1fr; }}
      .hero-stats {{ flex-direction: row; }}
      .hood-grid {{ grid-template-columns: 1fr; }}
      .footer-inner {{ grid-template-columns: 1fr; gap: 32px; }}
    }}
  </style>
</head>
<body>
  <header class="masthead">
    <div class="masthead-inner">
      <a href="/" class="masthead-brand">
        <span class="masthead-wire">The Pittsburgh Wire</span>
        <span class="masthead-title">Neighborhoods</span>
      </a>
      <nav class="masthead-nav">
        <a href="/">Home</a>
        <a href="/neighborhoods" class="active">Neighborhoods</a>
        <a href="/directory">Directory</a>
        <a href="/about">About</a>
      </nav>
    </div>
  </header>

  <div class="hero">
    <div class="hero-inner">
      <div>
        <div class="hero-eyebrow">The Pittsburgh Wire</div>
        <h1 class="hero-headline">Pittsburgh<span>Neighborhoods</span></h1>
        <p class="hero-sub">Explore the neighborhoods that make Pittsburgh one of the most livable cities in America. Local news, businesses, and stories from every corner of the Steel City.</p>
      </div>
      <div class="hero-stats">
        <div class="stat">
          <span class="stat-num">{len(NEIGHBORHOODS)}</span>
          <span class="stat-label">Neighborhoods</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-num">{total_articles}</span>
          <span class="stat-label">Articles</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-num">{total_biz}</span>
          <span class="stat-label">Businesses</span>
        </div>
      </div>
    </div>
  </div>

  <div class="breadcrumb">
    <a href="/">Home</a>
    <span class="sep">/</span>
    <span style="color:var(--light)">Neighborhoods</span>
  </div>

  <div class="content">
    <div class="hood-grid">
{cards_html}
    </div>
  </div>

  <footer class="footer">
    <div class="footer-inner">
      <div>
        <div class="footer-brand">The Pittsburgh Wire</div>
        <p class="footer-tagline">Good News, Only. Always Forward.</p>
        <p class="footer-copy">&copy; 2026 The Pittsburgh Wire. All rights reserved.</p>
      </div>
      <div>
        <div class="footer-heading">Sections</div>
        <ul class="footer-links">
          <li><a href="/">Home</a></li>
          <li><a href="/neighborhoods">Neighborhoods</a></li>
          <li><a href="/directory">Business Directory</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-heading">Popular Neighborhoods</div>
        <ul class="footer-links">
          <li><a href="/neighborhoods/lawrenceville">Lawrenceville</a></li>
          <li><a href="/neighborhoods/strip-district">Strip District</a></li>
          <li><a href="/neighborhoods/east-liberty">East Liberty</a></li>
          <li><a href="/neighborhoods/oakland">Oakland</a></li>
          <li><a href="/neighborhoods/downtown">Downtown</a></li>
          <li><a href="/neighborhoods/shadyside">Shadyside</a></li>
        </ul>
      </div>
    </div>
  </footer>
</body>
</html>'''
    return hub_html


def update_sitemap(new_urls):
    """Add new neighborhood URLs to sitemap.xml."""
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")
    new_entries = ""
    for url in new_urls:
        full_url = f"{SITE_URL}{url}"
        if full_url not in content:
            new_entries += f"""  <url>
    <loc>{full_url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
"""

    if new_entries:
        content = content.replace("</urlset>", new_entries + "</urlset>")
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Added {len(new_urls)} URLs to sitemap.xml")


def main():
    print("Pittsburgh Wire Neighborhood Page Generator")
    print("=" * 50)

    # Step 1: Scan content
    print("\nScanning articles...")
    articles = scan_articles()
    print(f"  Found {len(articles)} articles")

    print("Scanning directory...")
    businesses = scan_directory()
    print(f"  Found {len(businesses)} businesses")

    # Step 2: Map to neighborhoods
    print("\nMapping content to neighborhoods...")
    content_map = map_content_to_neighborhoods(articles, businesses)
    for nid, data in content_map.items():
        name = NEIGHBORHOODS[nid]["name"]
        print(f"  {name}: {len(data['articles'])} articles, {len(data['businesses'])} businesses")

    # Step 3: Generate pages
    print("\nGenerating neighborhood pages...")
    os.makedirs(NEIGHBORHOODS_DIR, exist_ok=True)
    new_urls = ["/neighborhoods"]

    for nid, ndata in NEIGHBORHOODS.items():
        slug = ndata["slug"]
        page_dir = os.path.join(NEIGHBORHOODS_DIR, slug)
        os.makedirs(page_dir, exist_ok=True)
        page_html = generate_neighborhood_page(nid, ndata, content_map)
        page_path = os.path.join(page_dir, "index.html")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"  Created /neighborhoods/{slug}/index.html")
        new_urls.append(f"/neighborhoods/{slug}")

    # Step 4: Generate hub page
    print("\nGenerating hub page...")
    hub_html = generate_hub_page(content_map)
    hub_path = os.path.join(NEIGHBORHOODS_DIR, "index.html")
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(hub_html)
    print("  Created /neighborhoods/index.html")

    # Step 5: Update sitemap
    print("\nUpdating sitemap...")
    update_sitemap(new_urls)

    print("\nDone! Generated pages for all neighborhoods.")
    print(f"Total: {len(NEIGHBORHOODS)} neighborhood pages + 1 hub page")


if __name__ == "__main__":
    main()
