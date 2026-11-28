import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const parks = require('../data/pittsburgh-parks.json');
const shell = require('../scripts/parks-shell.cjs');
const SITE = 'https://www.thepittsburghwire.com';
const CITY = 'https://www.pittsburghpa.gov/Recreation-Events/CitiParks/Our-Parks';
const PERMITS = 'https://www.pittsburghpa.gov/Recreation-Events/CitiParks/Park-Permits';
const RELEASE_AT = Date.parse('2026-11-28T04:32:00Z');
const MINUTE = 60_000;
const groups = [
  {slug: 'playgrounds', title: 'Pittsburgh Parks With Playgrounds', field: 'playgrounds', description: 'Find city parks with listed playgrounds and compare neighborhood locations.'},
  {slug: 'dog-parks', title: 'Pittsburgh Dog Parks and Off-Leash Areas', field: 'dog', description: 'Find off-leash areas listed by the city and check which park to visit.'},
  {slug: 'pools-and-spray-parks', title: 'Pittsburgh Parks With Pools and Spray Features', field: 'aquatics', description: 'Find parks with aquatics facilities and check the operator’s seasonal schedule.'},
  {slug: 'courts-and-fields', title: 'Pittsburgh Parks With Courts and Sports Fields', field: 'sports', description: 'Compare parks by listed courts and fields and find the city’s permit information.'},
  {slug: 'picnic-shelters', title: 'Pittsburgh Parks With Picnic Shelters', field: 'shelters', description: 'Find park shelters and check availability and permit requirements with the city.'},
  {slug: 'by-neighborhood', title: 'Pittsburgh Parks by Neighborhood', field: 'neighborhood', description: 'Browse Pittsburgh park addresses by the neighborhood names used in the city directory.'},
];
const featured = ['allegheny-commons-park', 'allegheny-riverfront-park', 'arsenal-park', 'august-wilson-park',
  'schenley-park', 'frick-park', 'highland-park', 'riverview-park', 'mellon-park'];
const order = [ ...parks.filter(park => featured.includes(park.slug)), ...parks.filter(park => !featured.includes(park.slug)) ];
const entries = [
  {kind: 'hub', slug: 'index', path: '/parks/'},
  ...groups.map(group => ({kind: 'group', slug: group.slug, path: '/parks/' + group.slug + '/', group})),
  ...order.map(park => ({kind: 'park', slug: park.slug, path: '/parks/' + park.slug + '/', park})),
].map((entry, index) => ({...entry, time: RELEASE_AT + index * MINUTE}));
if (new Set(entries.map(entry => entry.slug)).size !== 169) {
  throw new Error('The release requires 169 unique routes');
}
const bySlug = new Map(entries.map(entry => [entry.slug, entry]));

function escape(value) {
  return String(value).replace(/[&<>"']/g, char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
}
function link(url, label) {
  return '<a href="' + escape(url) + '">' + escape(label) + '</a>';
}
function list(items) {
  return '<ul>' + items.map(item => '<li>' + item + '</li>').join('') + '</ul>';
}
function document(entry, title, description, content) {
  const body = '<div class="breadcrumb">' + link('/', 'Home') + '<span>/</span>' +
    link('/parks/', 'Pittsburgh Parks') + '</div>' +
    '<header class="page-head"><h1 class="page-title">' + escape(title) +
    '</h1><p class="page-deck">' + escape(description) + '</p></header>' +
    '<main class="archive"><article class="service-guide">' + content + '</article></main>';
  const values = {TITLE: escape(title + ' | The Pittsburgh Wire'), DESCRIPTION: escape(description),
    CANONICAL: SITE + entry.path, BODY: body};
  return shell.replace(/%%(TITLE|DESCRIPTION|CANONICAL|BODY)%%/g, (token, key) => values[key]);
}
function parkLabel(entry) {
  return link(entry.path, entry.park.name) + ' · ' + escape(entry.park.address);
}
function render(entry, published) {
  const parkEntries = published.filter(item => item.kind === 'park');
  if (entry.kind === 'hub') {
    const categoryLinks = published.filter(item => item.kind === 'group').map(item => link(item.path, item.group.title));
    const content = (categoryLinks.length ? '<h2>Browse by amenity</h2>' + list(categoryLinks) : '') +
      (parkEntries.length ? '<h2>Browse park profiles</h2>' + list(parkEntries.map(parkLabel)) : '') +
      '<p>Addresses and facilities come from the city’s parks directory. Check current conditions before traveling.</p>' +
      '<p>' + link(CITY, 'Official CitiParks directory') + '</p>';
    return document(entry, 'Pittsburgh Parks Directory', 'Find Pittsburgh parks by location, playgrounds, courts, pools, dog areas, and shelters.', content);
  }
  if (entry.kind === 'group') {
    const {field, title, description} = entry.group;
    const publishedBySlug = new Map(parkEntries.map(item => [item.slug, item]));
    const matches = parks.filter(park => park[field]).sort((a, b) =>
      field === 'neighborhood' ? a.neighborhood.localeCompare(b.neighborhood) || a.name.localeCompare(b.name) : a.name.localeCompare(b.name));
    const summary = list(matches.map(park => {
      const match = publishedBySlug.get(park.slug);
      const label = match ? parkLabel(match) : escape(park.name + ' · ' + park.address);
      return label + ' · ' + escape(park[field]);
    }));
    return document(entry, title, description, summary + '<p>' + link(CITY, 'Check the full city directory for facility details') + '.</p>');
  }
  const park = entry.park;
  const facts = [['Address', [park.address, park.zip].filter(Boolean).join(', ')], ['Neighborhood', park.neighborhood],
    ['Playgrounds', park.playgrounds], ['Off-leash area', park.dog], ['Aquatics', park.aquatics],
    ['Courts and fields', park.sports], ['Shelters', park.shelters]];
  const details = '<section><h2>Location and listed amenities</h2><dl>' + facts.filter(([, value]) => value)
    .map(([label, value]) => '<dt><strong>' + label + '</strong></dt><dd>' + escape(value) + '</dd>').join('') + '</dl></section>';
  const nearby = parkEntries.filter(item => item.slug !== entry.slug && item.park.neighborhood === park.neighborhood);
  const resources = '<section><h2>Before you go</h2><p>' + link(CITY, 'Check the city’s park listing') +
    ' for facility details. ' + ((park.shelters || park.sports) ? link(PERMITS, 'Check permit and reservation options') + ' if planning a group event.' : '') + '</p></section>';
  return document(entry, park.name + ', Pittsburgh', 'Find ' + park.name + ' in Pittsburgh, with its listed location and amenities.', details + resources +
    (nearby.length ? '<section><h2>Other parks listed in the same area</h2>' + list(nearby.map(parkLabel)) + '</section>' : ''));
}

function send(request, body, status, type, retryAfter) {
  const headers = {'Content-Type': type, 'Cache-Control': 'no-store'};
  if (retryAfter) headers['Retry-After'] = String(retryAfter);
  return new Response(request.method === 'HEAD' ? null : body, {status, headers});
}

export function serve(request, now = Date.now()) {
  const url = new URL(request.url);
  const slug = url.pathname === '/parks-sitemap.xml' ? 'sitemap' :
    url.pathname.startsWith('/parks') ? (url.pathname.split('/').filter(Boolean)[1] ?? 'index') :
      url.searchParams.get('page');
  const published = entries.filter(entry => entry.time <= now);
  if (slug === 'sitemap' || url.pathname === '/parks-sitemap.xml') {
    const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
      published.map(entry => '<url><loc>' + SITE + entry.path + '</loc><lastmod>' +
        new Date(entry.time).toISOString() + '</lastmod></url>').join('') + '</urlset>';
    return send(request, xml, 200, 'application/xml; charset=utf-8');
  }
  const entry = bySlug.get(slug);
  if (!entry) return send(request, 'Park page not found.', 404, 'text/plain; charset=utf-8');
  if (entry.time > now) return send(request, 'This park page is scheduled for publication.', 404, 'text/plain; charset=utf-8',
    Math.ceil((entry.time - now) / 1000));
  return send(request, render(entry, published), 200, 'text/html; charset=utf-8');
}

export function GET(request) { return serve(request); }
export function HEAD(request) { return serve(request); }
