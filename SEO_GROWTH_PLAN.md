# Pittsburgh Wire search growth plan — September 22, 2026

## Positioning

Win useful Pittsburgh searches through original, source-checked reporting on local business, real estate, development, and neighborhoods. “All things Pittsburgh” is a long-term editorial ambition, not a keyword target or an indexation guarantee. Publishing many lightly researched pages would weaken the site's credibility. Google's [people-first guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) favors useful, reliable work with a clear audience.

## What this pass found

- The main sitemap contains 329 preferred, indexable URLs. Withdrawn guides and unverified directory profiles are excluded.
- Five section hubs used generic titles such as “Business News” and headings such as “Business.” They now identify the city and subject clearly.
- Eighteen neighborhood hubs held stale story lists and promoted withdrawn business profiles. Their cards now use published, place-specific stories and a short list of source-checked businesses with confirmed local connections. Counts reflect the rendered cards.
- A dedicated news sitemap now contains only articles from the last two calendar days. Google allows a separate news sitemap for better tracking; it must be regenerated as publishing continues. The standard sitemap remains the source for the full archive.
- The article publishing script now requires an outbound source link, rejects future publication dates, and matches structured-data author to the visible byline.
- Search Console's last known page-indexing totals predate the sitemap cleanup and cannot establish the current indexed share. A fresh export is needed after Google processes the current sitemap. No verified query-volume, ranking, or backlink dataset was available for this plan.

## Search intent clusters

These are editorial targets, not measured keyword volumes or difficulty scores. Each should earn a useful page through reporting or a regularly maintained hub, not a near-duplicate landing page.

In a qualitative search snapshot, [VisitPITTSBURGH](https://www.visitpittsburgh.com/neighborhoods/) had a broad neighborhood guide and [Pittsburgh Magazine](https://www.pittsburghmagazine.com/spring-2026-restaurant-openings/) maintained restaurant-opening coverage. The Wire should build depth in its own business and development beats, then connect those reports to specific neighborhoods. This observation is not a ranking or traffic comparison.

| Cluster | Reader intent | Existing home | Next useful addition |
| --- | --- | --- | --- |
| Pittsburgh business news | Follow local companies and openings | `/news/business/` | Weekly sourced roundup linking to original reports |
| Pittsburgh startup funding | Find rounds and investors | Business archive | Funding ledger with company, amount, date, and direct announcement |
| Pittsburgh robotics and AI | Track firms and hires | Business archive | Explain individual companies and cite current company records |
| Pittsburgh manufacturing expansion | Understand jobs and plants | Business archive | Project tracker with announced vs completed status |
| New Pittsburgh restaurants | Decide where to visit | Business archive and directory | Opening tracker with verified address and opening status |
| Pittsburgh development projects | Follow planned and active work | `/news/development/` | Status tracker linked to permits, URA records, and developers |
| Downtown Pittsburgh development | Understand block-level change | Downtown neighborhood hub | Map or address-based project list with dated sources |
| Pittsburgh affordable housing | Find real projects and units | Development and real estate archives | Explainer of active projects with agency records |
| Pittsburgh real estate news | Follow transactions and buildings | `/news/real-estate/` | Recurring sourced market brief |
| Pittsburgh neighborhood news | Discover relevant local stories | `/neighborhoods/` | Current, verified links and original local reporting |
| Lawrenceville business openings | Find new places | Lawrenceville hub | Address-checked opening log |
| Strip District development | Follow major projects | Strip District hub | Distinguish plans, approvals, construction, and openings |
| Oakland university expansion | Follow institutional projects | Oakland hub | University and permit-backed project timeline |
| North Side development | Follow housing and riverfront work | North Side hub | Source-checked project status and neighborhood context |
| Pittsburgh business directory | Find current organizations | `/directory/` | Expand the 21 verified profiles only after primary-source checks |

## Publishing standard

1. Verify the central claim with a primary record before drafting. Link that record in the article body.
2. Separate announcements, forecasts, construction, openings, and completed results in the headline and first paragraph.
3. Do not invent quotes, addresses, investment totals, visitor counts, or neighborhood ties. Attribute company projections.
4. Link each new article from the appropriate section and neighborhood hub. Use descriptive anchor text.
5. Correct or withdraw unsupported older pages before expanding a topic cluster.
6. Refresh the news sitemap whenever a new article is published; keep only the latest two calendar days.

## Next 90 days

**Weeks 1–2:** Recheck Search Console's sitemap and Page indexing reports after recrawl. Inspect a sample of “Discovered” and “Crawled, not indexed” URLs, then address the documented reason. Finish the newsletter opt-in test with a controlled address. Review the highest-traffic and newest unsourced articles first.

**Weeks 3–6:** Build one maintained development tracker and one verified openings tracker. Record a source URL and “checked on” date for every entry. Strengthen neighborhood hubs with firsthand observations, local organizations, transport context, and current original reporting. Prioritize neighborhoods with empty story and business sections.

**Weeks 7–12:** Publish recurring beats only where the team can maintain accuracy. Seek citations and links through original data, interviews, project timelines, and useful explainers; avoid buying links or mass-producing neighborhood variants.

**Measurement:** Track Search Console clicks, impressions, average position, indexed canonical URLs, and queries by topic cluster monthly. Track newsletter opt-ins only after the form-to-list flow is verified. Judge success by relevant readership and returning users, not the raw count of indexed pages.

## Search guidance

- [Google Search Central: helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search Central: build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google Search Central: news sitemap best practices](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap)
- [Google Search Central: sitemap `lastmod` and crawl timing](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)
