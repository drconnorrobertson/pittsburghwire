"""Validate exact reviewed source relationships, without trusting entire hosts."""
from datetime import date
from html import escape
from urllib.parse import urlsplit

MODEL = 'reviewed_links_v1'
RELATIONSHIPS = {'business_linked': 'Business-linked external provider',
                 'host_venue': 'Host venue information',
                 'official_chain': 'Official chain information',
                 'matched_listing': 'Separately matched provider listing'}

def evidence_errors(research, link):
    url = link.get('url', '')
    host = urlsplit(research.get('url', '')).hostname
    if urlsplit(url).hostname == host:
        return []
    evidence = link.get('evidence', {})
    errors = []
    if research.get('evidence_model') != MODEL:
        return ['official evidence link leaves corroborated host']
    if evidence.get('relationship') not in RELATIONSHIPS:
        errors.append('external evidence relationship missing or invalid')
    if evidence.get('target') != url:
        errors.append('external evidence does not bind the exact destination')
    source = evidence.get('source', '')
    if any(urlsplit(value).scheme != 'https' or not urlsplit(value).hostname
           for value in (url, source)):
        errors.append('external evidence requires HTTPS source and destination')
    if evidence.get('relationship') in {'business_linked', 'official_chain'} and urlsplit(source).hostname != host:
        errors.append('linked-source evidence must originate on the business website')
    if evidence.get('relationship') in {'host_venue', 'matched_listing'} and (source != url or evidence.get('business_url') != research.get('url')):
        errors.append('venue or matched-listing evidence requires its exact page and business URL')
    try:
        checked = date.fromisoformat(evidence.get('checked', ''))
        if checked > date.today():
            errors.append('external evidence check is in the future')
    except (ValueError, TypeError):
        errors.append('external evidence check date missing or invalid')
    if not evidence.get('note', '').strip() or not link.get('label', '').strip():
        errors.append('external evidence requires a specific label and review note')
    return errors

def reviewed_links_markup(row):
    research = row['official_research']
    if research.get('evidence_model') != MODEL:
        raise ValueError('An explicitly reviewed evidence model is required')
    items = []
    for kind, link in research.get('links', {}).items():
        if kind == 'careers':
            continue
        errors = evidence_errors(research, link)
        if errors:
            raise ValueError('; '.join(errors))
        evidence = link.get('evidence')
        detail = (' — ' + escape(RELATIONSHIPS[evidence['relationship']]) + '. ' +
                  escape(evidence['note']) + ' Relationship checked ' +
                  escape(evidence['checked']) + '.') if evidence else ' — Business website.'
        items.append('<li><a href="' + escape(link['url'], quote=True) +
                     '" rel="noopener noreferrer">' + escape(link['label']) + '</a>' + detail + '</li>')
    chain_only = all(link.get('evidence', {}).get('relationship') == 'official_chain' for kind, link in research.get('links', {}).items() if kind != 'careers')
    external = [link['evidence'] for kind, link in research.get('links', {}).items() if kind != 'careers' and link.get('evidence')]
    venue_only = bool(external) and all(e['relationship'] == 'host_venue' for e in external)
    scope = ('Venue information describes the host location; confirm business service availability separately.' if venue_only and not chain_only else 'Use the local location page for stand-specific details; the chain resources below describe general information.' if chain_only else 'A booking or shopping provider operates separately from this directory; confirm current terms on that provider’s page.')
    return ('<h2>Useful sources for ' + escape(row['name']) + '</h2>'
            '<p>The links below identify the business website and separately reviewed external sources. '
            + scope + '</p>'
            '<ul>' + ''.join(items) + '</ul>')
