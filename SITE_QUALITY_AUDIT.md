# Pittsburgh Wire quality audit — September 22, 2026

## Published content standard

- The Best Of hub promotes three researched guides. The 297 older pages that did not name recommended places now show a withdrawal notice, carry `noindex, follow`, and stay outside the sitemap. Their old claims and incorrect `LocalBusiness` structured data are no longer published. The original versions remain in Git history for later research.
- The directory promotes 21 profiles with current source links and concise checked summaries. Each of the 11 categories has at least one sourced profile. The 288 other legacy profiles with unchecked descriptions now show a neutral editorial review notice. Nine listings whose identity or website could not be corroborated remain separately labeled under review. All 297 review pages carry `noindex, follow` and are absent from the directory hub and sitemap.
- Three closed restaurant profiles remain available as labeled historical pages with `noindex, follow`. Four duplicate profile paths permanently redirect to a preferred profile.
- The eight newly restored directory profiles use current official sources: [Carnegie Robotics](https://www.carnegierobotics.com/about), [Chatham University](https://www.chatham.edu/about-us/), [Dollar Bank](https://locations.dollar.bank/headquarters/pittsburgh-headquarters), [Gecko Robotics](https://www.geckorobotics.com/contact), [Pamela's Diner](https://pamelasdiner.com/), [PJ Dick](https://pjdick.com/about), [PNC](https://investor.pnc.com/company-information/faqs), and [Primanti Bros.](https://restaurants.primantibros.com/locations/pa/pittsburgh). Three more fill previously empty categories: [Baum Boulevard Automotive](https://www.baumblvdauto.com/about), [Pittsburgh Cultural Trust](https://trustarts.org/pct_home/about), and [Walnut Capital](https://www.walnutcapital.com/contact).

## Verification

Run `python3 build_site.py` and `python3 quality_check.py` from the repository root. The quality check verifies every sitemap URL against its page canonical and robots tag, parses structured data, checks local links, confirms every sourced profile appears on the hub and its category page, and confirms withdrawn pages stay out of browse and search discovery. The latest local run checked 937 HTML pages, 35,920 local links, and 332 sitemap URLs with no errors. The builder is deterministic on a second run.

## Remaining editorial work

The legacy news archive has 263 article files, and 253 have no outbound source link. That absence alone does not prove the reporting is wrong, so this pass has not withdrawn those articles. Their claims, dates, and quotations need a separate source review before the archive can be called fully fact checked. Newsletter form delivery and Google Search Console indexing status also remain unverified; IndexNow acceptance only confirms URL submission.
