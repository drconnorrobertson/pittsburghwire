# Pittsburgh Wire search growth plan — September 22, 2026

## October 7, 2026 execution update

The directory expansion publishes 2,647 source-backed listings alongside 21 earlier profiles, for 2,668 total profiles. Coverage includes Pittsburgh mailing addresses and nearby communities; the page always states the listed address. Every added record has a name, category, address, phone, website, source, and checked date. The new profiles, 13 category hubs, and 61 focused service/community collections credit Dr. Connor Robertson. Seventy-four existing news articles now link to relevant profiles, and those profiles link back to the reporting.

These are useful directory records, not 2,647 original reported features. An additional depth pass corroborated 2,001 official websites, added business-site descriptions and useful navigation where available, and expanded contact guidance and collection context. The next editorial investment should add individual reporting, owner interviews, and verified local context to the businesses that readers actually search for. The source listing establishes published contact information, not a review score or proof of a personal visit.

### Measured starting point

Connected Google Search Console data for September 7–October 4, 2026 shows:

| Query | Clicks | Impressions | Average position |
| --- | ---: | ---: | ---: |
| opal grand buffet | 62 | 2,839 | 5.89 |
| opal grand buffet price | 35 | 173 | 1.55 |
| badamos sandwich shop | 9 | 150 | 4.48 |
| giulia pittsburgh | 9 | 89 | 3.29 |
| hotel bardo pittsburgh | 8 | 37 | 2.35 |

These are average positions across the reported period, not fixed current ranks. Google URL Inspection confirms the directory homepage was submitted and indexed; its last recorded crawl was October 5. That does not establish indexing of the new profiles.

### A practical route to broader Pittsburgh visibility

1. **Business-name searches:** Keep one accurate profile per distinct business/location. Improve contact details, service specifics, official booking/menu links, and related reporting. Preserve existing articles already receiving search traffic. Expand current source checks before calling a planned opening operational.
2. **Service discovery:** Maintain focused collections of real providers with explicit source categories. Prioritize accountants/bookkeepers, financial advisors, contractors, law firms, catering, and marketing. Add information that helps a reader compare providers; do not rank them without a documented basis.
3. **Neighborhood discovery:** Strengthen the existing neighborhood hubs with verified neighborhood assignments, current openings, independent shops, and original reporting. Mailing ZIP codes alone cannot establish a neighborhood. Community collections use the source's named mailing locality.
4. **Business and development news:** Maintain dated opening and development trackers with direct business announcements, permit records, and project-status distinctions. Build on the Wire's existing restaurant-opening search demand.
5. **Local authority:** Give businesses a useful, accurate profile they can choose to link to. Publish original interviews and factual project timelines that local organizations can cite. Outreach is a separate action requiring explicit messaging authorization; none is sent in this release.
6. **Measurement:** Compare non-overlapping 28-day windows. Track directory impressions/clicks, number of profiles receiving impressions, business-name query positions, service/community query positions, and sampled indexing verdicts. Flag pages with impressions but weak click-through for title/snippet improvements; investigate documented crawl/indexing failures before publishing more variants.

### Next 90 days: priorities, not scheduled commitments

**First 14 days:** Verify the release and sitemap receipt; inspect a representative sample after Google has time to crawl. Review the strongest existing business-name pages for source freshness and correct opening status. Add richer facts to the first 25 profiles with demonstrated demand.

**Days 15–45:** Produce 20 original owner/business features connected to the directory and location hubs. Maintain one restaurant-opening tracker and one development tracker. Seek voluntary local citations through useful reporting and accurate profiles.

**Days 46–90:** Expand the sectors and communities that show real demand. Refresh weak or stale entries and improve the comparison detail in service collections. Measure increases in search visibility and qualified readers; do not describe a first-place goal as an achieved rank.

### Indexing implementation

The full sitemap and directory sitemap expose every eligible profile. Both are declared in robots.txt. The IndexNow key is connected and its live file validated. The submission script waits for Vercel's current static content and submits sitemap URLs to IndexNow. An optional automatic workflow is prepared but not installed because the saved token lacks workflow scope. Google receives the live sitemaps through Search Console. Submission acceptance is not an indexing or ranking guarantee; ordinary business pages do not qualify for Google's restricted Indexing API.

The September assessment below is retained as historical context; its URL/profile counts and statement about unavailable Search Console query data predate this release.

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
