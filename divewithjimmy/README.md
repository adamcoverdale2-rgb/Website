# Dive With Jimmy — new website

A static, single-page site for [divewithjimmy.com](https://divewithjimmy.com), the SSI and BSAC dive centre in Kempston, Bedfordshire.

- `index.html` — page content
- `styles.css` — styling (no framework)
- `script.js` — mobile nav, course tabs, hire price toggle (pool / day / weekend), "Enquire" buttons that prefill the form, and an enquiry form that opens the visitor's email app addressed to info@divewithjimmy.com
- `assets/img/` — photos and logos copied from the current site and resized

No build step. Open `index.html` directly, or serve the folder:

```sh
python3 -m http.server 8000
```

## Content
Copy, course list, pool night details and hire prices come from the current divewithjimmy.com (November 2026).

## Check before going live
- **Phone number.** The current site shows 07538 051564, but its call link dials a US number (425-334-5956), which looks like a template mistake. This site uses 07538 051564.
- **Course prices.** Only the Open Water price (£400–£800, shown as "From £400") is listed on the current site. Add others if you want them shown.
- **Gas fill prices** and the **Dive Club** membership fee aren't included. Those pages weren't copied over.
- **Reviews.** The hero links to the Google reviews (5.0, 20 reviews). Update the count as it grows.
- **Booking.** The form opens an email. To take bookings or payments directly, link the Square shop or the SSI booking calendar instead.
