# Pittsburgh Wire quality audit — September 22, 2026

## Scope

Reviewed the homepage, news articles and indexes, business directory, neighborhood pages, Best of guides, weekly archive, shared mobile navigation, signup markup, structured data, canonical tags, and sitemap generation. This was a source audit with sitewide automated checks and representative page inspection. No signup form was submitted and no production performance or Google Search Console data was available.

## Changes on this branch

- The sitemap builder now reads each page's canonical tag. Before this change, 788 of 933 sitemap entries used a different URL form than their page canonical, mostly because of trailing slashes. The homepage canonical now uses its root URL with a slash. This aligns two discovery signals; it does not guarantee indexing or ranking changes.
- Three older news articles used `<meta name="canonical">`, which search engines do not treat as a canonical link. They now use `<link rel="canonical">`.
- The shared mobile menu now exposes its expanded state and controlled navigation to assistive technology, and Escape closes the menu and returns focus to its button.

## Main unresolved content issues

1. **Best of guides need editorial work.** All 300 guide pages inspected have two H1 headings, the same generic paragraph structure, and no link to a specific business directory profile. A sample page titled “Best Coffee Shops in Lawrenceville” names no coffee shops. The pages promise recommendations but provide general neighborhood copy. [Google's content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) asks whether a page provides original information and satisfies the reader's goal. Rewriting a smaller set of useful guides with named, verified businesses is the highest value next step. Whether to remove the remaining guides from the sitemap or mark them `noindex` needs an editorial decision because it changes search visibility for 300 URLs.
2. **Some directory profiles duplicate the same business.** At least S.W. Randall Toyes & Giftes, UPMC, and Construction Junction have duplicate profile names at separate URLs; Gaucho Parrilla also appears in two variants on the directory hub. Verify the preferred profile and business facts before consolidating or redirecting.
3. **The weekly archive is stale.** The latest listed edition is May 3, 2026 while the page promises a Saturday weekly delivery. Confirm the actual newsletter schedule and archive source before updating that claim.
4. **Signup completion has not been verified.** Forms point to Formspree. Several forms change their button label to “Subscribed” during submission, before a response is known. Testing a real subscription would send a message to an external service, so this audit did not submit one. The homepage's central form handles success and errors separately.
5. **Subscriber count needs a source.** Several pages state “Join 5,000+ readers.” Subscriber data was not available in this audit.

## Verification

- Site builder completes and remains deterministic on a second run.
- All 933 sitemap URLs are unique and match the exact canonical URL in their corresponding page.
- Existing JSON-LD blocks parse, and internal local links resolve in the source tree.
- The modified JavaScript was reviewed statically. Browser interaction, keyboard behavior, visual layout, and Core Web Vitals still need a browser run before merge.

Google describes sitemap URLs and `rel="canonical"` as signals for its selected canonical URL and recommends including the preferred URL in a sitemap; neither is an indexing guarantee. See [canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) and [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).
