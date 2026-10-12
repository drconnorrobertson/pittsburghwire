"""Maintain focused reader paths from stories with demonstrated search demand."""
from pathlib import Path
from html import escape
import re

PATHS = {
    'opal-grand-buffet-waterfront-homestead-pittsburgh': [
        ('/news/pittsburgh-buffet-restaurants-three-options/', 'Compare Pittsburgh buffet options'),
        ('/news/homestead-waterfront-new-development-pittsburgh/', 'Waterfront apartment development: documented plans'),
        ('/neighborhoods/homestead/', 'More Homestead reporting')],
    'badamos-dormont-sandwich-shop-italian-market': [
        ('/best/restaurants-in-dormont/', 'Explore restaurants in Dormont'),
        ('/news/giulia-bloomfield-pittsburgh-coastal-italian-lilith', 'Giulia in Bloomfield: restaurant details')],
    'homestead-waterfront-new-development-pittsburgh': [
        ('/news/opal-grand-buffet-waterfront-homestead-pittsburgh', 'Opal Grand Buffet: opening status, menu and prices'),
        ('/neighborhoods/homestead/', 'Explore Homestead news'),
        ('/news/development/', 'Follow Pittsburgh development projects')],
    'giulia-bloomfield-pittsburgh-coastal-italian-lilith': [
        ('/best/restaurants-in-bloomfield/', 'Explore restaurants in Bloomfield'),
        ('/neighborhoods/bloomfield/', 'More Bloomfield reporting')],
    'isalys-strip-district-pittsburgh-summer-2026': [
        ('/neighborhoods/strip-district/', 'Explore Strip District reporting'),
        ('/best/restaurants-in-strip-district/', 'Explore Strip District restaurants')],
    'city-edge-apartments-southside-pittsburgh': [
        ('/neighborhoods/south-side/', 'More South Side reporting'),
        ('/news/real-estate/', 'Follow Pittsburgh real estate news')],
    'esplanade-north-shore-pittsburgh-construction-2026': [
        ('/neighborhoods/north-side/', 'More North Side reporting'),
        ('/news/esplanade-phase-two-pittsburgh-north-side-2026/', 'Esplanade phase two coverage')],
}

def write(repo):
    root = Path(repo)
    for slug, links in PATHS.items():
        page = root / 'news' / slug / 'index.html'
        source = page.read_text()
        source = re.sub(r'<!-- search-pathways -->.*?<!-- /search-pathways -->\n?', '', source, flags=re.S)
        for href, _ in links:
            if not (root / href.strip('/') / 'index.html').exists():
                raise ValueError(f'Missing search pathway: {href}')
        body = '<!-- search-pathways --><section><h2>Explore related local coverage</h2><ul>'
        body += ''.join(f'<li><a href="{escape(href)}">{escape(label)}</a></li>' for href, label in links)
        body += '</ul></section><!-- /search-pathways -->\n'
        marker = '<div class="article-tags"'
        if marker not in source:
            marker = '</article>'
        if marker not in source:
            raise ValueError(f'Missing article container: {slug}')
        page.write_text(source.replace(marker, body + marker, 1))
    return len(PATHS)
