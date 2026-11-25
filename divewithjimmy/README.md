# Dive With Jimmy — new website

A static, multi-page site for [divewithjimmy.com](https://divewithjimmy.com), the SSI and BSAC dive centre in Kempston, Bedfordshire. No server or framework is needed: open `index.html`, or serve the folder:

```sh
python3 -m http.server 8000
```

## Pages
- `index.html`: home page
- `courses/index.html`: all 50 courses by category, with search and an SSI/BSAC filter
- `courses/<course>.html`: one page per course, with price, a Square "Book now" button, facts, what's included, and a link to the SSI or BSAC standards
- `pool-nights.html`, `gas-fills.html`, `servicing.html`, `equipment-hire.html`, `expeditions.html`, `dive-club.html`, `about.html`, `contact.html`

## Editing content
All pages are generated, so don't edit the `.html` files directly.

- **Courses:** edit `src/courses.json` (text, facts, prices, Square checkout codes, related courses)
- **Other pages:** edit the functions in `src/build.py`

Then rebuild:

```sh
python3 src/build.py
```

Styling is in `styles.css` and behaviour in `script.js` (menu, course filter, hire price switch, contact form).

## Content sources
Text, prices and Square checkout links come from the current divewithjimmy.com (November 2026). Course details were cross-checked against divessi.com and bsac.com. **See `COURSE-AUDIT.md`** for every correction and the items to confirm before going live.

Photos are Dive With Jimmy's own, copied from the current site and resized.

## Booking
- Course "Book now" buttons go straight to that course's Square checkout.
- Courses without their own checkout link show "Enquire", which opens the contact form with the course filled in.
- "Book a course" and "Book a pool night" go to the Square shop (divewithimmy.square.site; the shop's real address has no J).
- The contact form opens the visitor's email app, addressed to info@divewithjimmy.com.
