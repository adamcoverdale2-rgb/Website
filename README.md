# Scuba Murcia — website redesign

A static, single-page redesign of [scubamurcia.com](https://www.scubamurcia.com) (PADI 5 Star dive centre, La Manga, Spain).

- `index.html` — page content
- `styles.css` — styling (no framework)
- `script.js` — nav, course tabs, scroll reveals, depth gauge, enquiry form (opens the visitor's email app)
- `assets/` — favicon

No build step. Open `index.html` directly, or serve the folder:

```sh
python3 -m http.server 8000
```

## Content
Copy, prices, dive sites and team details come from the current scubamurcia.com (October 2026).
Photos are linked from the existing site's image host (`static.wixstatic.com`); each photo has a gradient fallback.

## Before going live
- Download the photos into `assets/` rather than linking them from Wix, so the new site doesn't depend on the old one.
- Add photos for Louise and Kate (they show initials for now).
- Add opening hours if you want them shown. The current site doesn't list them.
