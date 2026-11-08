# ELIA downtown directory correction

Search Console (Web, October 10–November 6, 2026) mapped `elia downtown pittsburgh` to `/directory/elia-estiatorio/`: 1,299 impressions, 11 clicks, 0.8% CTR, average position 9.3. This identifies the page to improve; it does not establish that its title alone caused the low CTR.

The existing page quoted an old expected-opening announcement and linked to Elia Mediterranean Grille in Warrendale. The current VisitPITTSBURGH listing instead links to https://eliaestiatoriopgh.com/ and names the same downtown address and phone.

Sources checked in the signed-in browser November 8, 2026:
- https://www.visitpittsburgh.com/directory/elia-estiatorio/ — current downtown listing and official website link.
- https://eliaestiatoriopgh.com/ — 120 Fifth Avenue, Pittsburgh PA 15222; (412) 866-3542; current menu, ordering and reservation links; downtown contact email.
- https://eliaestiatoriopgh.com/food-menu — separate lunch/dinner menus and current selections.
- https://www.eliamediterraneangrille.com/ — explicitly identifies the separate Warrendale address. Do not use its menu, phone or hours for downtown.

The correction removes the outdated quotation, links the downtown website, adds short source-backed visitor guidance, and gives the page a specific title and description. Preserve the original October 7 publication date; update verification/modification and both sitemap dates to November 8. No exact opening date, current price, review score or firsthand dining claim is introduced. The generic title fallback is unchanged for all other profiles.

Validation: production pipeline plus full quality check; compare the separate catalog checker with the unchanged 24-error baseline; verify rendered title/canonical, original publication date, updated modification date and correct outbound host. Only the edited source, profile, and its two sitemap records belong in this PR.
