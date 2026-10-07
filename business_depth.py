"""Useful profile context built from sourced facts and corroborated official links."""
from html import escape
from collections import Counter

QUESTIONS={
'food-and-drink':('Plan a meal or gathering', ['Which menu is available for the date and location you have in mind?', 'Does the business accept reservations, offer takeout, or handle group orders?', 'Ask about dietary requirements directly; a category listing does not establish allergen handling.']),
'hotels-and-lodging':('Compare a stay', ['Confirm the property address and room or accommodation type before booking.', 'Ask which parking, accessibility, check-in, and cancellation conditions apply to your dates.', 'Check whether taxes, deposits, and any property fees are included in the quoted total.']),
'finance':('Prepare for a financial-services conversation', ['Identify the specific service you need and the office or professional who handles it.', 'Ask how fees are calculated, what ongoing service includes, and which qualifications apply.', 'Request written terms and confirm any relevant licensing or registration independently.']),
'health-and-wellness':('Prepare for a visit', ['Confirm which services are available at this exact location.', 'Ask about appointment requirements, provider credentials, accessibility, and payment arrangements.', 'For clinical care, confirm insurance participation with both the provider and your insurer.']),
'real-estate':('Clarify a property enquiry', ['Identify the property, community, or transaction you want help with.', 'Ask whether the listed office serves that location and who will handle your enquiry.', 'Request current availability, fees, contractual terms, and any relevant licensing details.']),
'education':('Compare a learning program', ['Ask which programs, age groups, and enrollment dates apply to your needs.', 'Confirm the location, schedule, fees, and any prerequisites.', 'Check accreditation, instructor qualifications, accessibility, or other requirements relevant to the program.']),
'arts-and-culture':('Plan an outing', ['Confirm the event or activity calendar and whether advance tickets are required.', 'Check the entrance location, parking or transit arrangements, and accessibility information.', 'Ask about age restrictions, group arrangements, and cancellation or weather policies when relevant.']),
'retail':('Plan a purchase', ['Check whether the item or product category you want is stocked at this location.', 'Ask about collection, delivery, returns, warranties, and any ordering lead time.', 'Confirm opening hours and whether the listed address is a shop, showroom, office, or fulfillment location.']),
'automotive':('Prepare an automotive enquiry', ['Describe the vehicle, service, or purchase you are considering.', 'Ask whether the location handles that make, model, or type of work.', 'Request a written price breakdown, timing estimate, and applicable warranty or sales terms.']),
'nonprofit-and-community':('Find the right community contact', ['Ask which programs are currently available and who is eligible.', 'Confirm whether appointments, referrals, membership, or registration are required.', 'For volunteering or donations, use the organization’s own contact information and published instructions.']),
'professional-services':('Define the work you need', ['Describe the intended outcome, timing, and any location requirements.', 'Ask who will deliver the work and what experience or qualifications apply.', 'Request a clear scope, fee structure, deliverables, and written engagement terms.']),
}
QUESTIONS['tech']=('Scope a technology project',['Describe the systems, users, and business problem involved.', 'Ask which products or services are offered and how implementation, support, and security responsibilities are divided.', 'Request a written scope covering costs, delivery timing, data ownership, and ongoing support.'])
QUESTIONS['trades-and-services']=('Prepare a service request',['Describe the work, property location, and timing before requesting an estimate.', 'Ask whether the business serves your address and which permits, credentials, or insurance are relevant.', 'Request a written scope covering materials, labor, exclusions, scheduling, and warranty terms.'])
NAV_LABELS={'menu':'Menus','services':'Services','products':'Products','about':'Business background','contact':'Contact information','appointments':'Appointments','reservations':'Reservations','locations':'Locations','events':'Events','membership':'Membership','request-quote':'Request an estimate','careers':'Careers'}

def profile_depth(row,data):
 e=escape;name=e(row['name']);city=e(row['city']);d=row.get('official_research',{});parts=[]
 if d.get('status')=='corroborated':
  url=e(d['url'],quote=True)
  topics=d.get('topics',[])
  if topics:
   links=', '.join(f'<a href="{e(t["url"],quote=True)}" rel="noopener noreferrer">{e(t["label"])}</a>' for t in topics)
   parts.append(f'<h2>Topics on the official website</h2><p>{name}’s website links to information on {links}. These links describe what the website covers; confirm the service, product, or program with the business for your particular needs.</p>')
  links=d.get('links',{})
  useful=[(typ,v) for typ,v in links.items() if typ!='careers'][:6]
  if useful:
   items=''.join(f'<li><a href="{e(v["url"],quote=True)}" rel="noopener noreferrer">{NAV_LABELS[typ]}</a></li>' for typ,v in useful)
   parts.append(f'<h2>Useful pages from {name}</h2><p>Go directly to the business’s published information rather than relying on a directory category alone:</p><ul>{items}</ul><p>These official links were checked on October 7, 2026. Details on the business’s website can change independently of this profile.</p>')
 heading,questions=QUESTIONS.get(row['category'],QUESTIONS['professional-services'])
 parts.append(f'<h2>{e(heading)} with {name}</h2><p>Use the listed category, <strong>{e(row["source_category"])}</strong>, as a starting point for your enquiry. It is a source-directory classification, so it does not establish every service offered at this address.</p><ul>'+''.join('<li>'+e(q)+'</li>' for q in questions)+'</ul>')
 same=[x for x in data.values() if x['city']==row['city'] and x['category']==row['category']]
 if len(same)>1:
  parts.append(f'<h2>Compare businesses in {city}</h2><p>This profile is one of {len(same)} listings in this broad category with a {city} source address. The related profiles below provide other names and contact details to explore. Compare the actual services, location, and suitability of each business; listings are not ranked by quality or price.</p>')
 return '\n'.join(parts)

def collection_depth(section,slugs,data):
 rows=[data[s] for s in slugs];parts=[]
 if section=='locations':
  counts=Counter(r['category'] for r in rows)
  from business_catalog import LABELS
  text=', '.join(f'{LABELS[c]} ({n})' for c,n in counts.most_common())
  parts.append(f'<h2>What this local directory covers</h2><p>The {len(rows)} profiles below span these broad categories: {escape(text)}. This is coverage of sourced listings rather than a count of every business operating in the community.</p><h2>Use the full address</h2><p>Community names here follow the address in the source listing. Postal cities can cross municipal boundaries. Open a profile to check its full street address and map link, then confirm whether the business has a public storefront or works by appointment.</p>')
 else:
  counts=Counter(r['city'] for r in rows)
  text=', '.join(f'{c} ({n})' for c,n in counts.most_common(12))
  parts.append(f'<h2>Where the listed providers are based</h2><p>The source addresses for this collection include {escape(text)}. An office location does not establish a provider’s service area. Contact the business to ask whether it handles work at your address.</p><h2>Compare the specific service</h2><p>Open the individual profiles to see each source category and official website. Businesses grouped under one service label can have different specialties, capabilities, qualifications, and pricing. Describe the work you need and request a written scope or applicable terms before choosing a provider.</p>')
 parts.append('<h2>How to check a listing</h2><p>Each profile identifies its source and the date the listing details were checked. Where an official website could be corroborated, the profile includes direct links to useful information. Contact the business for current availability and use the correction link if an address or contact detail has changed.</p>')
 return '\n'.join(parts)


def article_body_span(markup):
    import re
    m=re.search(r'<(article|div)\b[^>]*class="article-body"[^>]*>',markup)
    if not m:return None
    tag=m[1];depth=1
    for t in re.finditer(r'</?'+tag+r'\b[^>]*>',markup[m.end():]):
        depth+=-1 if t[0].startswith('</') else 1
        if depth==0:return m.end(),m.end()+t.start()
    return None
