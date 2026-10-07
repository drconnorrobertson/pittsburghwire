# Source-backed Pittsburgh business directory

The October 7, 2026 expansion adds 1,000 sourced listings to the 21 previously checked profiles. Listings include Pittsburgh and nearby communities. They are sourced from VisitPITTSBURGH and the Pittsburgh North Regional Chamber, not personal reviews or endorsements. Founder and publisher Dr. Connor Robertson is the author of the new profiles and collections.

`data/businesses.json` holds published business facts and source links. Missing owners, founding dates, staff counts, ratings, prices, and hours are intentionally omitted. The short attributed source excerpt never exceeds 20 words. Keep sources and checked dates current when updating records. Do not assert a storefront is open solely because a mailing address exists.

Run `python3 build_site.py`, then `python3 quality_check.py` and `python3 check_business_catalog.py`. The build writes profiles, category pages, service/community collections, related-news links, and both the full and directory sitemaps. Commit all generated changes together.

After a main-branch push, Vercel publishes the static files. Run `python3 submit_indexnow.py --wait-for-deploy` to verify the deployed content and live key file before submitting sitemap URLs. HTTP 200/202 means submission acceptance, never confirmed indexing. An optional workflow was prepared separately; the saved GitHub token lacks workflow scope, so it is not installed.

Google Search Console uses the registered full-site and directory sitemaps. Submit the existing live sitemap URLs with the connected GSC Wizard tool after a substantial release; Google also discovers them through robots.txt. Google's restricted JobPosting/BroadcastEvent Indexing API is not appropriate for ordinary business profiles. Google decides whether and when pages enter search results.

Ranking priorities: useful facts and verified service details, original local reporting, sensible profile-to-article links, accurate service/community collections, and real links from local businesses that choose to reference their profiles. Measure business-name impressions, clicks, and average position separately from broader service searches. No page count or submission guarantees first place.
