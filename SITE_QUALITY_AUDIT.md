# Pittsburgh Wire quality audit — September 22, 2026

## Scope

Reviewed the homepage, news articles and indexes, business directory, neighborhood pages, Best of guides, weekly archive, shared mobile navigation, signup markup, structured data, canonical tags, and sitemap generation. This was a source audit with sitewide automated checks and representative desktop and mobile browser inspection. No signup form was submitted and no Google Search Console data was available.

## Changes on this branch

- The sitemap builder now reads each page's canonical tag. Before this change, 788 of 933 sitemap entries used a different URL form than their page canonical, mostly because of trailing slashes. The homepage canonical now uses its root URL with a slash. This aligns two discovery signals; it does not guarantee indexing or ranking changes.
- Three older news articles used `<meta name="canonical">`, which search engines do not treat as a canonical link. They now use `<link rel="canonical">`.
- The shared mobile menu now exposes its expanded state and controlled navigation to assistive technology, and Escape closes the menu and returns focus to its button.
- Replaced the Best of hub's 300 generic guide links with two researched guides that name five businesses each, give locations and reasons to visit, and link to primary business sites. The other 298 pages remain accessible but now carry `noindex, follow` and are omitted from the sitemap. This is a deliberate search visibility change: those pages did not identify the businesses their titles promised. The site builder regenerates this state consistently.
- Removed unverified subscriber-count and Saturday delivery claims from signup copy. The supposed Weekly archive contained summaries but no links to readable editions, so its page now presents the newsletter signup without those archive entries. Native Formspree forms no longer display a success state before a response. The forms themselves were not submitted in this audit.
- Repaired four broken article links: three category breadcrumbs and one related-story link.

## Main unresolved content issues

1. **The remaining 298 Best of pages need research or retirement.** They still use generic neighborhood copy and do not name the recommended businesses. Their `noindex` state prevents the hub and sitemap from promoting them while keeping existing URLs available. [Google's content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) emphasizes original, useful information that satisfies the reader's goal. Future guides should follow the researched format and cite current primary sources.
2. **Some directory profiles duplicate the same business.** At least S.W. Randall Toyes & Giftes, UPMC, and Construction Junction have duplicate profile names at separate URLs; Gaucho Parrilla also appears in two variants on the directory hub. Verify the preferred profile and business facts before consolidating or redirecting.
3. **Newsletter delivery and archive source remain unknown.** Confirm the actual mailing schedule and obtain readable editions before restoring an archive.
4. **Signup completion has not been verified.** Forms point to Formspree. Testing a real subscription would send a message to an external service, so this audit did not submit one. The homepage's central form handles success and errors separately; the native forms rely on Formspree's response page.

## Verification

- Site builder completes and remains deterministic on a second run.
- All 635 sitemap URLs are unique, match the exact canonical URL in their corresponding page, and exclude `noindex` pages.
- Existing JSON-LD blocks parse, and 44,608 local links resolve in the source tree after fixing four broken links.
- The two researched guides and Best of hub were inspected at desktop and phone widths. The mobile menu opens and exposes its expanded state. Core Web Vitals and live subscription delivery remain unverified.

Google describes sitemap URLs and `rel="canonical"` as signals for its selected canonical URL and recommends including the preferred URL in a sitemap; neither is an indexing guarantee. See [canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) and [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).
