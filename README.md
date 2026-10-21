# Scuba Murcia — website redesign

A static, single-page redesign of [scubamurcia.com](https://www.scubamurcia.com) (PADI 5 Star dive centre, La Manga, Spain).

- `index.html` — page content
- `styles.css` — styling (no framework)
- `script.js` — nav, course tabs, scroll reveals, depth gauge, enquiry form (opens the visitor's email app)
- `assets/logos/` — Scuba Murcia and training agency logos (PADI, SSI, TDI, PSAI)
- `assets/img/` — dive site and team photos

No build step. Open `index.html` directly, or serve the folder:

```sh
python3 -m http.server 8000
```

## Content
Copy, prices, dive sites and team details come from the current scubamurcia.com (October 2026).
Logos and photos were copied from the current site into `assets/`, so nothing loads from the old Wix site.

## Before going live
- Add photos for Louise and Kate (they show initials for now).
- Add opening hours if you want them shown. The current site doesn't list them.
