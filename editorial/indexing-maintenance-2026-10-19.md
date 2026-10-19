# Indexing maintenance — October 19, 2026

## Scope and evidence

Authorized maintenance of existing coverage; no new articles or volume targets.
Current source commit: `b9c5a9e91a8dea747900821b2b41eef2c66c9c65`.

Private exports, URL decisions, HTTP checks, per-URL inspection evidence and the
complete review list are retained outside Git in
`../reports/indexing-audit-2026-10-19/`. Raw Search Console exports are not committed.

The historical discovered/crawled exports contain 96 news URL rows, representing
91 distinct article paths. All 91 canonical URLs returned HTTP 200 with matching
live canonical metadata and no noindex directive. Direct Google URL inspection
confirmed 51 indexed and 24 not indexed. Sixteen remain unverified after Google
reported that the property's daily inspection quota was exhausted. The separately
inspected fireplace-showroom guide is indexed. These are Web indexing statuses,
not proof of Google News app/site inclusion or current search rankings.

The overview displayed an October 11 update date; individual example crawl dates
can be later. Historical issue exports must not be treated as a current index
status for every URL. The confirmed unindexed list is predominantly older coverage
without body-source links. Reverify source records and current reader usefulness
before promoting or submitting those articles. Do not mass-request weak coverage.
Resume the sixteen remaining direct checks only after the quota resets.

## Changes

- Restore 21 currently broken reported URLs: 18 old section routes and three
  renamed-story routes, with permanent redirects to matching destinations.
- Send five legacy `?section=` filters to the requested section archive rather
  than the unfiltered news archive. Both root slash forms are supported.
- Retain truthful 404 responses for 15 retired tag URLs, two author URLs and six
  old story URLs without a verified equivalent. Do not redirect these to home.
- Eleven reported 404 URLs already returned 200 before changes; preserve them.
- Add relevant topic-hub links for 35 existing comparison guides, expanding the
  existing Best Of collection from 45 to 80 distinct guides. No new guide pages,
  publication dates, factual claims or independently awarded rankings are created.
- Normalize internal article links to each article's existing canonical at the end
  of the deployment build, preserving queries, fragments and external links.
- Match the directory sitemap entry to the paginated directory's canonical.
- Validate that every directory pagination page is reachable through HTML links,
  and that all 2,801 verified profiles remain discoverable across the directory.

## Validation

Source quality check: 3,973 pages, zero errors.
Full production-build quality check: 4,019 pages, 187,505 local links,
47,774 structured-data URLs, 3,453 sitemap URLs, zero errors.
All redirect destinations exist; no duplicate route/condition pairs.
Canonical-link fixtures cover ownership, external links, query strings, fragments
and idempotence. All 35 article diffs were checked to contain only the added
comparison-hub link. Article body reporting and publication dates are preserved.

Deployment verified READY on exact source commit b9c5a9e in Production:
`dpl_8pLDJ68ut3rEU6pBYnPs6dsiRtRS`. All 55 reported paths checked live: 21
repaired paths permanently redirect to matching HTTP 200 destinations; 23 intended
404s remain, and 11 previously working paths remain available. All five section
queries select their matching archive. Relevant hub links and the directory
canonical sitemap entry were verified live. Automatic deployment
`dpl_AzDMWPSghurVoCMtNF3GyVhqjAaV` remained in initialization for over
five minutes without build output. Canceled only that unpublished deployment
and retried the exact same source commit once in the existing project, Production
environment, through the signed-in Vercel dashboard. Connector build-log access
returned team-scope 403; no repeated connector request was made.
Main sitemap changed to SHA-256
`9e23e9f7b263db84bfc8bea0331ce0ba007c3231628c7c042edeb232c2d7833d` and was accepted by the
Google Search Console browser UI after live verification. The News and directory
sitemap hashes are unchanged and were not resubmitted. Dated hash history is in
`sitemap-submission-pending.json`. Submission does not establish indexing. No
restricted Indexing API calls or bulk indexing requests were made.
