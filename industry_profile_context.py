"""Persist sourced context and guide links for featured industry businesses."""
from pathlib import Path
import re

CONTEXT = {
    '412-plumbing': ('Plan a plumbing enquiry', 'Confirm the service area, diagnostic charges and the scope of the first visit. Explain whether the property is residential or commercial and request a confirmed appointment window.', 'https://www.412plumbing.com/', 'best-plumbers-pittsburgh-editorial-picks'),
    'phipps-conservatory-and-botanical-gardens': ('Event planning at Phipps', 'Phipps lists garden and conservatory event settings and a separate Garden Center in Mellon Park. Its pricing page currently directs enquiries to the events team. Confirm the exact venue and request current terms.', 'https://www.phipps.conservatory.org/plan-your-event/', 'best-event-venues-pittsburgh-editorial-picks'),
    'baum-boulevard-automotive': ('Maintenance and diagnostic enquiries', 'Baum Boulevard Automotive publishes preventive maintenance, breakdown repair and diagnostics, with an online appointment option. Call 412-682-1866 to confirm the work and drop-off arrangements for your vehicle.', 'https://www.baumblvdauto.com/', 'best-auto-repair-pittsburgh-editorial-picks'),
    'union-fitness': ('Membership comparison', 'Compare the equipment-focused Fitness Center tier with UF Unlimited, which adds the full class schedule. Confirm access, class booking and current membership terms directly.', 'https://unionfitness.com/new-memberships/', 'best-gyms-pittsburgh-editorial-picks'),
    'south-hills-movers': ('Prepare a moving enquiry', 'Provide both addresses, the move date, inventory and access details. Request a written scope distinguishing transport, packing and any storage arrangements.', 'https://www.southhillsmovers.com/', 'best-moving-companies-pittsburgh-editorial-picks'),
}


def write(repo):
    for slug, (heading, detail, source, guide) in CONTEXT.items():
        page = Path(repo) / 'directory' / slug / 'index.html'
        markup = page.read_text()
        markup = re.sub(r'<!-- INDUSTRY_CONTEXT_START -->.*?<!-- INDUSTRY_CONTEXT_END -->', '', markup, flags=re.S)
        block = f'''<!-- INDUSTRY_CONTEXT_START --><section class="profile-copy"><h2>{heading}</h2><p>{detail}</p><p><a href="{source}" rel="noopener noreferrer">Official service information</a> · Checked October 10, 2026.</p><p>Featured in our <a href="/news/{guide}/">Pittsburgh industry comparison guide</a>. Inclusion is an editorial selection, not an independent award or a guarantee of service quality.</p></section><!-- INDUSTRY_CONTEXT_END -->'''
        assert '</main>' in markup
        page.write_text(markup.replace('</main>', block + '</main>', 1))
    return len(CONTEXT)
