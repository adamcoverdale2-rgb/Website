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

## Before going live
- Confirm prices, opening hours and the enquiry email (`scuba.murcia@outlook.com`).
- Swap the gradient dive-site tiles for real underwater photos.
- Add genuine customer reviews if wanted.
