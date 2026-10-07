# Source-backed Pittsburgh business directory

The October 7, 2026 expansion adds 2,647 sourced listings to the 21 previously checked profiles. Listings include Pittsburgh and nearby communities. They are sourced from VisitPITTSBURGH and the Pittsburgh North, Pittsburgh Airport Area, Westmoreland County, and Beaver County chambers, not personal reviews or endorsements. Founder and publisher Dr. Connor Robertson is the author of the new profiles and collections.

`data/businesses.json` holds published business facts and source links. Missing owners, founding dates, staff counts, ratings, prices, and hours are intentionally omitted. The short attributed source excerpt never exceeds 20 words. Keep sources and checked dates current when updating records. Do not assert a storefront is open solely because a mailing address exists.

Run `python3 build_site.py`, then `python3 quality_check.py` and `python3 check_business_catalog.py`. The build writes profiles, category pages, service/community collections, related-news links, and both the full and directory sitemaps. Commit all generated changes together.

After a main-branch push, Vercel publishes the static files. Run `python3 submit_indexnow.py --wait-for-deploy` to verify the deployed content and live key file before submitting sitemap URLs. HTTP 200/202 means submission acceptance, never confirmed indexing. An optional workflow was prepared separately; the saved GitHub token lacks workflow scope, so it is not installed.

Google Search Console uses the registered full-site and directory sitemaps. Submit the existing live sitemap URLs with the connected GSC Wizard tool after a substantial release; Google also discovers them through robots.txt. Google's restricted JobPosting/BroadcastEvent Indexing API is not appropriate for ordinary business profiles. Google decides whether and when pages enter search results.

Ranking priorities: useful facts and verified service details, original local reporting, sensible profile-to-article links, accurate service/community collections, and real links from local businesses that choose to reference their profiles. Measure business-name impressions, clicks, and average position separately from broader service searches. No page count or submission guarantees first place.

## Profile depth and evidence

The October 7 depth pass adds official-website evidence to 2,001 of 2,668 profiles. This includes 1,986 catalog businesses and 15 earlier profiles. The catalog has 1,567 attributed website excerpts, 1,753 profiles with useful official navigation links, and 440 with specific official-site topics. Unavailable or uncorroborated sites are recorded as such; do not invent descriptions or topics for them.

`business_depth.py` renders category-specific enquiry guidance and local comparison context from existing records. `original_profile_depth.py` extends the earlier 21 pages using `data/original-businesses.json`. The article connector handles both older div-based bodies and current article elements; 74 news stories carry dated source-linked directory context. Historical reporting dates and facts are preserved. This work improves directory usefulness and navigation; it is not 2,668 individually reported company features or a guarantee of indexing.

Store only public source facts, bounded excerpts, corroboration status, and useful URLs in the repository. Raw research responses belong in scratch storage. Keep attributed website excerpts plus topic labels within 25 words per website response. Run the quality and catalog checks after rebuilding; they validate output and evidence links.
