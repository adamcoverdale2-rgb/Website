#!/usr/bin/env python3
"""Builds the Dive With Jimmy static site from src/courses.json and the page
content below. Run from anywhere:  python3 src/build.py
Output: the .html files in the site folder (index.html, courses/, etc.)."""
import json
import re
from html import escape as e
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = json.loads((SITE / "src" / "courses.json").read_text())
SHOP = "https://divewithimmy.square.site"
CHECKOUT = DATA["checkout_base"]
PHONE, PHONE_TEL = "07538 051564", "+447538051564"
EMAIL = "info@divewithjimmy.com"
CATS = DATA["categories"]
COURSES = DATA["courses"]
BY_SLUG = {c["s"]: c for c in COURSES}
CAT = {c["id"]: c for c in CATS}

# Upcoming sessions from Jimmy's SSI / Scubago calendar (refresh with src/whatson.py)
_EV = SITE / "src" / "events.json"
EVENTS_DATA = json.loads(_EV.read_text()) if _EV.exists() else {"events": [], "fetched": ""}
SCUBAGO = EVENTS_DATA.get("calendar", "https://www.scubago.com/center/744483")
SSI_CAL = "https://my.divessi.com/extern/events/744483/"
# SSI programme codes used in the calendar -> course page
PROGRAMS = {"TS-P": "try-scuba-diving", "TFRD": "try-freediving", "SC-DRY": "ssi-dry-suit-diving",
            "SC-EAN": "ssi-enriched-air-nitrox", "SC-SR": "ssi-diver-stress-rescue",
            "SC-CCRTXR-AP": "ssi-ccr-technical-extended-range", "OWD": "ssi-open-water-diver",
            "SD": "ssi-scuba-diver", "BD": "ssi-basic-diver", "SC-DEEP": "ssi-deep-diving",
            "SC-NAV": "ssi-navigation", "SC-NLV": "ssi-night-limited-visibility", "SC-PB": "ssi-perfect-buoyancy",
            "SC-WRECK": "ssi-wreck-diving", "SC-SSU": "ssi-scuba-skills-update", "SKD": "ssi-snorkel-diver",
            "BFRD": "ssi-basic-freediver", "SC-RR": "ssi-react-right", "SC-CCR-AP": "ssi-ccr-diving"}


def event_slug(ev):
    if ev.get("program") in PROGRAMS:
        return PROGRAMS[ev["program"]]
    t = ev["title"].lower()
    if "pool night" in t:
        return "pool"
    for c in COURSES:
        if c["n"].lower().replace("ssi ", "") == t:
            return c["s"]
    return ""


from datetime import date as _date
TODAY = _date.today().isoformat()
EVENTS = [dict(ev, slug=event_slug(ev)) for ev in EVENTS_DATA["events"] if ev.get("end", ev.get("start", "")) >= TODAY]


def fmt_date(ev, short=False):
    from datetime import date as d
    a = d.fromisoformat(ev["start"]); b = d.fromisoformat(ev.get("end", ev["start"]))
    f = "%a %-d %b" if short else "%A %-d %B %Y"
    return a.strftime(f) if a == b else f"{a.strftime('%-d %b')} – {b.strftime('%-d %b %Y')}"


def event_card(ev, root):
    from datetime import date as d
    a = d.fromisoformat(ev["start"])
    link = ""
    if ev["slug"] == "pool":
        link = f'<a href="{root}pool-nights.html">About pool nights</a>'
    elif ev["slug"]:
        link = f'<a href="{root}courses/{ev["slug"]}.html">Course details</a>'
    price = f'£{ev["price"]:,.0f}' if ev.get("price") else ""
    return f'''<li class="ev">
  <div class="ev__date"><span>{a.strftime("%a")}</span><strong>{a.day}</strong><span>{a.strftime("%b")}</span></div>
  <div class="ev__body"><h3>{e(ev["title"])}</h3><p class="ev__when">{fmt_date(ev)}{" · " + price if price else ""}</p>
  <p class="ev__links"><a class="btn btn--sm" href="{e(ev["url"])}">Book this date</a>{link}</p></div>
</li>'''

NAV = [
    ("courses/index.html", "Courses", "courses"),
    ("whats-on.html", "What's on", "whatson"),
    ("pool-nights.html", "Pool nights", "pool"),
    ("gas-fills.html", "Gas & kit", "services"),
    ("expeditions.html", "Expeditions", "expeditions"),
    ("dive-club.html", "Dive club", "club"),
    ("about.html", "About", "about"),
    ("contact.html", "Contact", "contact"),
]


def buy_url(c):
    if c.get("buy_url"):
        return c["buy_url"]
    return CHECKOUT + c["buy"] if c.get("buy") else ""


def price_text(c):
    p = c.get("price", "")
    if c.get("from") and "–" in p:
        return "From " + p.split("–")[0].strip()
    return p


def header(root, active):
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        if key == "courses":
            sub = "".join(f'<li><a href="{root}courses/index.html#{c["id"]}">{e(c["name"])}</a></li>' for c in CATS)
            items.append(f'<li class="has-sub"><a href="{root}{href}"{cur}>{label}</a><ul class="sub">{sub}<li><a href="{root}courses/index.html">All courses →</a></li></ul></li>')
        elif key == "services":
            sub = "".join(f'<li><a href="{root}{h}">{l}</a></li>' for h, l in [("gas-fills.html", "Air &amp; gas fills"), ("servicing.html", "Cylinder &amp; equipment servicing"), ("equipment-hire.html", "Equipment hire"), (SHOP, "Shop")])
            items.append(f'<li class="has-sub"><a href="{root}{href}"{cur}>{label}</a><ul class="sub">{sub.replace(root + SHOP, SHOP)}</ul></li>')
        else:
            items.append(f'<li><a href="{root}{href}"{cur}>{label}</a></li>')
    items.append(f'<li class="nav__cta"><a class="btn btn--sm" href="{SHOP}">Book a course</a></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="nav__inner wrap">
    <a class="brand" href="{root}index.html"><img src="{root}assets/img/logo-mark.png" alt="" width="576" height="498"><span>Dive With Jimmy</span></a>
    <button class="nav__toggle" aria-expanded="false" aria-controls="nav-menu"><span class="sr-only">Menu</span><span class="bar"></span><span class="bar"></span></button>
    <nav aria-label="Main"><ul class="nav__menu" id="nav-menu">{"".join(items)}</ul></nav>
  </div>
</header>'''


def footer(root):
    cols = "".join(f'<li><a href="{root}courses/index.html#{c["id"]}">{e(c["name"])}</a></li>' for c in CATS)
    return f'''<footer class="footer">
  <div class="wrap footer__grid">
    <div>
      <a class="brand" href="{root}index.html"><img src="{root}assets/img/logo-mark.png" alt="" width="576" height="498"><span>Dive With Jimmy</span></a>
      <p>SSI &amp; BSAC scuba diving centre<br>82 College Street, Kempston<br>Bedfordshire MK42 8LU</p>
      <p><a href="tel:{PHONE_TEL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <div><h2>Courses</h2><ul>{cols}</ul></div>
    <div><h2>Dive centre</h2><ul>
      <li><a href="{root}whats-on.html">What's on</a></li>
      <li><a href="{root}pool-nights.html">Pool nights</a></li>
      <li><a href="{root}gas-fills.html">Air &amp; gas fills</a></li>
      <li><a href="{root}servicing.html">Servicing</a></li>
      <li><a href="{root}equipment-hire.html">Equipment hire</a></li>
      <li><a href="{root}expeditions.html">Expeditions</a></li>
      <li><a href="{root}dive-club.html">Dive club</a></li>
      <li><a href="{SHOP}">Book &amp; shop</a></li>
    </ul></div>
    <div><h2>About</h2><ul>
      <li><a href="{root}about.html">About us</a></li>
      <li><a href="{root}contact.html">Contact</a></li>
      <li><a href="https://www.divessi.com/en/home">SSI</a></li>
      <li><a href="https://www.bsac.com/">BSAC</a></li>
      <li><a href="https://divewithjimmy.com/terms-conditions/">Terms</a></li>
      <li><a href="https://divewithjimmy.com/privacy-policy/">Privacy</a></li>
    </ul></div>
  </div>
  <p class="wrap small footer__copy">© <span class="yr">2026</span> Dive With Jimmy</p>
</footer>'''


def page(path, title, desc, body, active="", root="", og_img="assets/img/team.jpg"):
    html = f'''<!doctype html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#ffffff">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{root}{og_img}">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mulish:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}styles.css">
<script>document.documentElement.classList.replace('no-js','js')</script>
</head>
<body>
{header(root, active)}
<main id="main">
{body}
</main>
{footer(root)}
<script src="{root}script.js"></script>
</body>
</html>
'''
    out = SITE / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)


def page_head(root, eyebrow, h1, lede, img=None, crumbs=None):
    bg = f'<img class="phead__bg" src="{root}assets/img/{img}" alt="">' if img else ""
    cr = ""
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
            f'<li><a href="{h}">{e(t)}</a></li>' for h, t in crumbs) + "</ol></nav>"
    return f'''<section class="phead{' phead--img' if img else ''}">{bg}
  <div class="wrap phead__inner">{cr}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    {f'<p class="lede">{lede}</p>' if lede else ''}
  </div>
</section>'''


def card(c, root):
    facts = dict(c["facts"])
    meta = []
    if facts.get("Minimum age"):
        meta.append(f'<span>Age {e(facts["Minimum age"].split(" ")[0])}+</span>' if facts["Minimum age"][0].isdigit() else '<span>All ages</span>')
    if facts.get("Max depth"):
        meta.append(f'<span>{e(facts["Max depth"].split(" ")[0].rstrip(","))}</span>')
    pt = c.get("price", "")
    base = re.sub(r"\([^)]*(upgrade|bundle)[^)]*\)", "", pt, flags=re.I)
    base = " · ".join(x for x in base.split("·") if not re.search(r"upgrade|recert", x, re.I))
    amounts = [float(x.replace(",", "")) for x in re.findall(r"£([\d,]+(?:\.\d+)?)", base)]
    if len(amounts) == 1 and base.strip() != pt.strip():
        pt = f"£{amounts[0]:,.0f}"
    if len(amounts) > 1:
        pt = f"From £{min(amounts):,.0f}"
    return f'''<li class="ccard" data-agency="{c["a"]}" data-name="{e(c["n"].lower())}">
  <a href="{root}courses/{c["s"]}.html">
    <img class="ccard__img" src="{root}assets/img/{c["img"]}" alt="" loading="lazy">
    <span class="ccard__body">
    <span class="badge badge--{c["a"].lower()}">{c["a"]}</span>
    <h3>{e(c["n"])}</h3>
    <p>{e(c["lede"])}</p>
    <span class="ccard__foot"><span class="ccard__meta">{"".join(meta)}</span><strong>{e(pt) if pt else "Enquire"}</strong></span>
    </span>
  </a>
</li>'''


# ---------------------------------------------------------------- course pages
def course_page(c):
    root = "../"
    cat = CAT[c["c"]]
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in c["facts"])
    body = "".join(f"<p>{e(p)}</p>" for p in c.get("body", []))
    for key in ("list", "list2"):
        if c.get(key):
            body += f'<h2 class="h3">{e(c.get(key + "_title", ""))}</h2><ul class="ticks">' + "".join(f"<li>{e(x)}</li>" for x in c[key]) + "</ul>"
    inc = ""
    if c.get("inc"):
        inc += f'<div class="incl"><h2 class="h3">What\'s included</h2><p>{e(c["inc"])}</p>'
        if c.get("extra"):
            inc += f'<p class="small"><strong>Extra costs:</strong> {e(c["extra"])}</p>'
        inc += "</div>"
    bu = buy_url(c)
    enquire = f'{root}contact.html?course={e(c["n"]).replace(" ", "+")}'
    if bu:
        actions = f'<a class="btn btn--block" href="{bu}">Book now</a><a class="btn btn--ghost btn--block" href="{enquire}">Ask a question</a>'
    else:
        actions = f'<a class="btn btn--block" href="{enquire}">Enquire about this course</a>'
    price = c.get("price") or "Ask for a price"
    parts = [p.strip() for p in price.split("·")]
    price_html = "".join(f'<p class="aside__price{" aside__price--sm" if len(parts) > 1 or len(p) > 14 else ""}">{e(p)}</p>' for p in parts)
    ref = ""
    if c.get("ref"):
        ref = f'<p class="small aside__ref">Training to <a href="{c["ref"]}" rel="noopener">{c["a"]} standards ↗</a></p>'
    upcoming = [ev for ev in EVENTS if ev["slug"] == c["s"]][:4]
    if upcoming:
        rows = "".join(f'<li><a href="{e(ev["url"])}"><span>{fmt_date(ev, True)}</span><span>Book →</span></a></li>' for ev in upcoming)
        next_dates = f'<div class="aside__card aside__dates"><p class="aside__label">Next dates</p><ul>{rows}</ul><a class="small" href="{root}whats-on.html">Full calendar →</a></div>'
    else:
        next_dates = f'<div class="aside__card aside__dates"><p class="aside__label">Dates</p><p class="small">No dates listed right now. <a href="{enquire}">Ask us</a> and we\'ll arrange one: we run every course, even for one student.</p><a class="small" href="{root}whats-on.html">See what\'s on →</a></div>'
    rel = [BY_SLUG[s] for s in c.get("rel", []) if s in BY_SLUG]
    rel_html = ""
    if rel:
        rel_html = f'<section class="section section--tight"><div class="wrap"><h2>Where next?</h2><ul class="cgrid">{"".join(card(r, root) for r in rel)}</ul></div></section>'
    html = page_head(root, f'<span class="badge badge--{c["a"].lower()}">{c["a"]}</span> {e(cat["name"])}', e(c["n"]), e(c["lede"]), c["img"],
                     [(root + "index.html", "Home"), (root + "courses/index.html", "Courses"), (root + "courses/index.html#" + cat["id"], cat["name"])])
    html += f'''<section class="section section--course">
  <div class="wrap course">
    <div class="course__main prose">{body}{inc}</div>
    <aside class="aside">
      <div class="aside__card">
        <p class="aside__label">Price</p>
        {price_html}
        <div class="aside__actions">{actions}</div>
        <dl class="aside__facts">{facts}</dl>
        {ref}
      </div>
      {next_dates}
    </aside>
  </div>
</section>
{rel_html}
<section class="ask"><div class="wrap ask__inner"><div><h2>Not sure this is the right course?</h2><p>Tell us about your diving so far and we'll point you in the right direction.</p></div><a class="btn" href="{enquire}">Ask Jimmy</a></div></section>'''
    desc = f'{c["n"]} at Dive With Jimmy, Kempston, Bedfordshire. {c["lede"]}'
    page(f"courses/{c['s']}.html", f'{c["n"]} | Dive With Jimmy', desc, html, "courses", root, "assets/img/" + c["img"])


# ---------------------------------------------------------------- courses index
def courses_index():
    root = "../"
    chips = "".join(f'<li><a href="#{c["id"]}">{e(c["name"])}</a></li>' for c in CATS)
    secs = ""
    for cat in CATS:
        cs = [c for c in COURSES if c["c"] == cat["id"]]
        secs += f'''<section class="cat" id="{cat["id"]}">
  <div class="cat__head"><h2>{e(cat["name"])}</h2><p>{e(cat["blurb"])}</p></div>
  <ul class="cgrid">{"".join(card(c, root) for c in cs)}</ul>
</section>'''
    body = page_head(root, f"{len(COURSES)} courses · SSI &amp; BSAC", "All courses",
                     "From a first try in the pool to 60m trimix and rebreather diving. Every course is taught in small groups: no more than 4 students per instructor, and we'll run any course for just one student.")
    body += f'''<section class="section section--tight">
  <div class="wrap">
    <div class="filter">
      <ul class="chips chips--nav">{chips}</ul>
      <div class="filter__tools">
        <label class="search"><span class="sr-only">Search courses</span><input type="search" id="course-search" placeholder="Search courses"></label>
        <div class="seg" role="radiogroup" aria-label="Agency">
          <button role="radio" aria-checked="true" data-agency="all">All</button>
          <button role="radio" aria-checked="false" data-agency="SSI">SSI</button>
          <button role="radio" aria-checked="false" data-agency="BSAC">BSAC</button>
        </div>
      </div>
    </div>
    {secs}
    <p class="empty" hidden>No courses match. <a href="../contact.html">Ask us</a> and we'll help.</p>
  </div>
</section>'''
    page("courses/index.html", "Scuba Diving Courses | Dive With Jimmy, Bedfordshire",
         "Every SSI and BSAC course at Dive With Jimmy: learn to dive, freediving, specialties, technical, rebreather, wreck and professional training.", body, "courses", root)


# ---------------------------------------------------------------- home
def home():
    root = ""
    cats = "".join(f'''<li class="tile"><a href="courses/index.html#{c["id"]}"><img src="assets/img/{c["img"]}" alt="" loading="lazy"><span><strong>{e(c["name"])}</strong><small>{len([x for x in COURSES if x["c"] == c["id"]])} courses</small></span></a></li>''' for c in CATS)
    pop = "".join(card(c, root) for c in COURSES if c.get("popular"))
    body = f'''<section class="hero">
  <img class="hero__bg" src="assets/img/team.jpg" alt="" width="959" height="640">
  <div class="hero__inner wrap">
    <p class="eyebrow">SSI &amp; BSAC dive centre · Kempston, Bedfordshire</p>
    <h1>From your first breath to <span class="hl">100&nbsp;metres.</span></h1>
    <p class="lede">Bedfordshire's award-winning scuba centre. Small groups, ex-military attention to detail, and instructors who'll teach you as patiently in the pool as they will on a trimix wreck dive.</p>
    <div class="cta"><a class="btn" href="{SHOP}">Book a course</a><a class="btn btn--ghost" href="courses/index.html">See all {len(COURSES)} courses</a></div>
    <a class="rating" href="https://www.google.com/search?q=Dive+With+Jimmy+Kempston+reviews"><span class="stars" aria-hidden="true">★★★★★</span><span><strong>5.0 on Google</strong> · 20 reviews</span></a>
  </div>
</section>
<section class="promises" aria-label="Why dive with us">
  <ul class="wrap promises__grid">
    <li><strong>4 : 1</strong><span>Max students per instructor</span></li>
    <li><strong>1</strong><span>Student is enough. We run every course, even for one.</span></li>
    <li><strong>Nitrox</strong><span>Included as standard on Open Water and Ocean Diver</span></li>
    <li><strong>100m</strong><span>Instructor-qualified on open and closed circuit</span></li>
  </ul>
</section>
<section class="section">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Courses</p><h2>Pick where you want to start.</h2><p>SSI and BSAC training, from a first try in the pool to professional and rebreather courses.</p></div>
    <ul class="tiles">{cats}</ul>
  </div>
</section>
{coming_up(root)}
<section class="section section--alt">
  <div class="wrap">
    <div class="head head--row"><div><p class="eyebrow">Most popular</p><h2>Where most divers start</h2></div><a class="more" href="courses/index.html">All courses →</a></div>
    <ul class="cgrid">{pop}</ul>
  </div>
</section>
<section class="split">
  <div class="wrap split__grid">
    <div>
      <p class="eyebrow">Every Tuesday</p>
      <h2>Pool nights in Bedford</h2>
      <p>Sole use of the 3.8m dive pit at Robinson Pool, 7–8:30pm. Practise skills, try new kit or just get wet midweek. £15, or free for Dive Club members.</p>
      <a class="btn" href="pool-nights.html">Pool night details</a>
    </div>
    <div>
      <p class="eyebrow">Worldwide</p>
      <h2>Expeditions</h2>
      <p>HMHS Britannic, technical wreck weeks in Greece, Scapa Flow, the Farne Islands, and Bikini Atoll in 2030. Small groups with gases, boat fees and guiding included.</p>
      <a class="btn btn--ghost" href="expeditions.html">See the calendar</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap about-teaser">
    <img src="assets/img/jimmy.jpg" alt="Jimmy kitted up on a closed circuit rebreather" width="853" height="570" loading="lazy">
    <div>
      <p class="eyebrow">About us</p>
      <h2>Military attention to detail. A genuine love of the water.</h2>
      <p>Jimmy learned to dive with the British Army in Cyprus. Today he's qualified to 100m on open and closed circuit, and has run trips to Truk Lagoon and Bikini Atoll. With Emma leading our snorkel and Blue Oceans work, we'll look after you from your first lesson.</p>
      <a class="more" href="about.html">Meet the team →</a>
    </div>
  </div>
</section>
{reviews()}
{gallery(root)}
{club_band(root)}
{contact_band(root)}'''
    page("index.html", "Dive With Jimmy | Scuba Diving Centre, Kempston, Bedfordshire",
         "Bedfordshire's award-winning SSI and BSAC dive centre. Learn to dive, freedive, go technical or rebreather to 100m. Max 4 students per instructor.", body, "", root)


def coming_up(root):
    if not EVENTS:
        return ""
    cards = "".join(event_card(ev, root) for ev in EVENTS[:6])
    return f'''<section class="section">
  <div class="wrap">
    <div class="head head--row"><div><p class="eyebrow">What's on</p><h2>Coming up</h2><p>Courses and sessions Jimmy has booked in. Pick a date and book online.</p></div><a class="more" href="{root}whats-on.html">Full calendar →</a></div>
    <ul class="evs">{cards}</ul>
  </div>
</section>'''


GALLERY = [("gallery/clownfish.jpg", "Clownfish in an anemone"), ("photos/wreck-planes.jpg", "Diver over aircraft wreckage"), ("gallery/nudibranch-pink.jpg", "Nudibranch"),
           ("gallery/soft-coral.jpg", "Soft coral"), ("gallery/leopard-shark.jpg", "Leopard shark"), ("photos/turtle.jpg", "Hawksbill turtle"),
           ("gallery/telegraph.jpg", "Ship's telegraph on a wreck"), ("gallery/mantis-shrimp.jpg", "Mantis shrimp"), ("gallery/jellyfish.jpg", "Jellyfish"),
           ("gallery/moray.jpg", "Moray eel"), ("gallery/divers-bw.jpg", "Divers on a wreck"), ("gallery/starfish.jpg", "Starfish and urchin"),
           ("gallery/heian-maru.jpg", "Name plate on the Heian Maru wreck"), ("gallery/cleaner-shrimp.jpg", "Cleaner shrimp")]


def gallery(root, title="Beneath the surface", n=14):
    items = "".join(f'<li><img src="{root}assets/img/{f}" alt="{e(a)}" loading="lazy"></li>' for f, a in GALLERY[:n])
    return f'''<section class="section section--alt gallery-sec">
  <div class="wrap">
    <div class="head head--center"><p class="eyebrow">From our dives</p><h2>{title}</h2></div>
    <ul class="gallery">{items}</ul>
  </div>
</section>'''


def reviews():
    rs = [("Peter Orton", "Outstanding service, teaching and expertise. Dived with Jimmy and his team in the training pool at Bedford and open water at Stoney Cove."),
          ("Chris Shrubb", "Just wrapped up three scuba courses back-to-back with Jimmy, and honestly, what a legend."),
          ("Adan Banga", "I had Jimmy put on my radar a while ago by a chap I bumped into a lot at Wraysbury. Got in touch with him and he was immediately super helpful.")]
    items = "".join(f'<li class="review"><span class="stars" aria-label="5 stars">★★★★★</span><blockquote>{e(t)}</blockquote><p>{e(n)} · Google review</p></li>' for n, t in rs)
    return f'''<section class="section">
  <div class="wrap">
    <div class="head head--center"><p class="eyebrow">5.0 on Google · 20 reviews</p><h2>What our divers say</h2></div>
    <ul class="reviews">{items}</ul>
    <p class="center"><a class="more" href="https://www.google.com/search?q=Dive+With+Jimmy+Kempston+reviews">Read all reviews on Google →</a></p>
  </div>
</section>'''


def whats_on():
    root = ""
    body = page_head(root, "Calendar", "What's on", "Courses, try dives and pool nights Jimmy has booked in. Choose a date to book it online through Scubago, SSI's booking site.", "photos/diver-clear.jpg")
    if EVENTS:
        months = {}
        for ev in EVENTS:
            months.setdefault(ev["start"][:7], []).append(ev)
        from datetime import date as d
        lists = "".join(f'<h2 class="month">{d.fromisoformat(k + "-01").strftime("%B %Y")}</h2><ul class="evs evs--list">{"".join(event_card(ev, root) for ev in v)}</ul>' for k, v in months.items())
    else:
        lists = '<p>No sessions are listed right now. Check the live calendar below or get in touch.</p>'
    body += f'''<section class="section section--tight"><div class="wrap">
  <div class="whatson">
    <div>{lists}
      <p class="small">Dates from Jimmy's SSI calendar, last updated {e(EVENTS_DATA.get("fetched", ""))}. The live calendar below always has the latest.</p>
    </div>
    <aside class="note">
      <h2 class="h3">Can't make these dates?</h2>
      <p>We run every course, even for one student. Tell us when suits you and we'll arrange it.</p>
      <p><a class="btn" href="contact.html">Ask about dates</a></p>
      <p class="small">Every Tuesday is <a href="pool-nights.html">pool night</a> at Robinson Pool, Bedford.</p>
    </aside>
  </div>
  <div class="live">
    <div class="head head--row"><div><p class="eyebrow">Live from SSI</p><h2>Full calendar</h2></div><a class="more" href="{SCUBAGO}">Open on Scubago →</a></div>
    <iframe src="{SSI_CAL}" title="Dive With Jimmy events calendar on SSI" loading="lazy"></iframe>
  </div>
</div></section>'''
    page("whats-on.html", "What's On | Dive With Jimmy, Bedfordshire", "Upcoming scuba courses, try dives and pool nights at Dive With Jimmy. Book a date online.", body, "whatson")


def club_band(root):
    return f'''<section class="club"><div class="wrap club__inner">
  <div><p class="eyebrow">Dive Club</p><h2>Keep diving after your course.</h2><p>Two pool sessions a month, 25% off hire, member socials and a personal diver development plan. From £20 a month, no contract.</p></div>
  <a class="btn btn--dark" href="{root}dive-club.html">Join the club</a>
</div></section>'''


def contact_band(root):
    return f'''<section class="section section--tight"><div class="wrap ask__inner ask__inner--plain">
  <div><h2>Ready to get in the water?</h2><p>Book and pay online, or get in touch and we'll help you choose. Call <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p></div>
  <div class="cta cta--tight"><a class="btn" href="{SHOP}">Book online</a><a class="btn btn--ghost" href="{root}contact.html">Contact us</a></div>
</div></section>'''


# ---------------------------------------------------------------- simple pages
def pool_dates():
    evs = [ev for ev in EVENTS if ev["slug"] == "pool"][:4]
    if not evs:
        return ""
    rows = "".join(f'<li><a href="{e(ev["url"])}"><span>{fmt_date(ev, True)}</span><span>Book →</span></a></li>' for ev in evs)
    return f'<div class="aside__card aside__dates"><p class="aside__label">Next pool nights</p><ul>{rows}</ul></div>'


def pool_nights():
    body = page_head("", "Every Tuesday", "Pool nights at Robinson Pool", "A great social evening for snorkellers, freedivers and scuba divers, with sole use of the dive pit in Bedford.", "photos/diver-clear.jpg")
    body += f'''<section class="section"><div class="wrap split__grid">
  <div class="prose">
    <p>We use the pool time to run courses, and to give everyone a chance to try new kit or just have a splash. The dive pit goes down to 3.8m.</p>
    <p>The cost is £15 for the evening, unless you're on a course with us. Dive Club members get pool access free.</p>
    <p>Meet at the rear entrance, next to the car park, just before 6:45pm. Parking is free.</p>
    <div class="cta"><a class="btn" href="{SHOP}">Book a pool night</a><a class="btn btn--ghost" href="dive-club.html">Join the club</a></div>
    <h2 class="h3">Courses we run on pool nights</h2>
    <ul class="ticks"><li><a href="courses/try-scuba-diving.html">Try Scuba Diving</a></li><li><a href="courses/try-freediving.html">Try Freediving</a></li><li><a href="courses/ssi-snorkel-diver.html">SSI Snorkel Diver</a></li><li><a href="courses/ssi-basic-freediver.html">SSI Basic Freediver</a></li><li><a href="courses/ssi-scuba-skills-update.html">SSI Scuba Skills Update</a></li></ul>
  </div>
  <div>
  <dl class="ticket">
    <div><dt>When</dt><dd>Tuesdays, 7:00–8:30pm</dd></div>
    <div><dt>Where</dt><dd>Robinson Pool, Bedford</dd></div>
    <div><dt>Arrive</dt><dd>Just before 6:45pm, rear entrance by the car park</dd></div>
    <div><dt>Depth</dt><dd>3.8m dive pit</dd></div>
    <div><dt>Cost</dt><dd>£15 <small>· free for Dive Club members and students on a course</small></dd></div>
    <div><dt>Parking</dt><dd>Free</dd></div>
  </dl>
  {pool_dates()}
  </div>
</div></section>'''
    page("pool-nights.html", "Pool Nights | Dive With Jimmy, Bedford", "Tuesday pool nights at Robinson Pool, Bedford, 7–8:30pm. Sole use of the 3.8m dive pit. £15, free for Dive Club members.", body, "pool")


def services_nav(cur):
    items = [("gas-fills.html", "Air &amp; gas fills"), ("servicing.html", "Servicing"), ("equipment-hire.html", "Equipment hire")]
    return '<ul class="chips chips--nav chips--tabs">' + "".join(f'<li><a href="{h}"{" aria-current=page" if h == cur else ""}>{l}</a></li>' for h, l in items) + "</ul>"


def table(caption, rows, head=None, cls=""):
    th = ""
    if head:
        th = "<thead><tr>" + "".join(f'<th scope="col">{h}</th>' for h in head) + "</tr></thead>"
    tb = "".join("<tr>" + f'<th scope="row">{r[0]}</th>' + "".join(f"<td>{x}</td>" for x in r[1:]) + "</tr>" for r in rows)
    return f'<table class="ptable {cls}"><caption>{caption}</caption>{th}<tbody>{tb}</tbody></table>'


def gas_fills():
    sizes232 = ["Up to 4L", "5.7–7L", "10–12L", "15L / T7", "T10 / T12"]
    sizes300 = ["Up to 3L", "5–7L", "10–12L / T7", "T10 / T12"]
    p232 = {"Air": ["£3", "£4.50", "£5.50", "£6.50", "£11"], "28%": ["£4", "£6", "£8", "£11.75", "£13.50"], "32%": ["£4.75", "£7.50", "£12", "£16.75", "£22"], "36%": ["£5.50", "£9.25", "£15.25", "£21.50", "£28.50"], "40%": ["£6.50", "£10.75", "£18.50", "£26.50", "£35"]}
    p300 = {"Air": ["£4", "£7", "£9", "£12"], "28%": ["£6", "£8.75", "£11", "£19"], "32%": ["£7.25", "£11.50", "£15.75", "£27.25"], "36%": ["£8.50", "£14.25", "£20", "£35.75"], "40%": ["£9.50", "£16.75", "£24.25", "£44.25"]}
    t1 = table("Up to 232 bar", [[s] + [p232[g][i] for g in p232] for i, s in enumerate(sizes232)], ["Cylinder", "Air", "Up to 28%", "Up to 32%", "Up to 36%", "Up to 40%"], "ptable--wide")
    t2 = table("Up to 300 bar", [[s] + [p300[g][i] for g in p300] for i, s in enumerate(sizes300)], ["Cylinder", "Air", "Up to 28%", "Up to 32%", "Up to 36%", "Up to 40%"], "ptable--wide")
    t3 = table("Oxygen, trimix &amp; argon", [["Oxygen", "3p per litre"], ["Helium", "6p per litre"], ["Argon", "2p per litre"], ["Air top-up (if needed)", "£3"]])
    t4 = table("HPA &amp; PCP air rifle fills", [["Up to 3L", "£4"], ["Up to 7L", "£6"], ["Up to 12L", "£7"]])
    body = page_head("", "Gas, servicing &amp; hire", "Air &amp; gas fills", "Breathing air, nitrox up to 100%, trimix and argon, plus HPA and PCP air rifle fills while you wait.", "gas.jpg")
    body += f'''<section class="section section--tight"><div class="wrap">{services_nav("gas-fills.html")}
  <div class="split__grid split__grid--top">
    <div class="prose">
      <p>Our filling and blending facility runs on an L&amp;W 450 compressor with a 4-whip filling panel and a 300 bar whip, filling 5 cylinders at 450 litres per minute. With our NRC booster pump we can supply breathing air, Enriched Air Nitrox up to 100%, trimix blends and argon for suit inflation.</p>
      <p>Every fill is checked for quality and purity. You must show a certification for the gas you're asking for. Not qualified for nitrox or trimix yet? <a href="courses/ssi-enriched-air-nitrox.html">We can teach you</a>.</p>
      <p class="small">Before leaving, please analyse your mix and record it in the gas log. Any discrepancies must be raised at the point of sale. Prices may change without notice.</p>
    </div>
    <div class="note"><h2 class="h3">Only pay for the gas you get</h2><p>Oxygen, helium and argon are charged by the litre we put in, plus an air top-up if needed. If your cylinder arrives with 100 bar of oxygen and we fill to 230 bar, you only pay for 130 bar.</p></div>
  </div>
  <div class="tables">{t1}{t2}</div>
  <div class="tables tables--2">{t3}{t4}</div>
</div></section>'''
    page("gas-fills.html", "Air & Gas Fills | Dive With Jimmy, Kempston", "Air, nitrox, trimix, oxygen and argon fills in Kempston, Bedfordshire, plus HPA and PCP air rifle fills. Full price list.", body, "services")


def servicing():
    t1 = table("Cylinder servicing", [["Hydrostatic test with valve service", "£52"], ["Visual inspection with valve service", "£40"], ["Cylinder &amp; valve oxygen cleaning (with test)", "£20"], ["Cylinder oxygen cleaning (without test)", "£40"], ["Twinset surcharge", "£14"], ["Failure charge", "£15"], ["Shot blasting", "£30"], ["Rust charge", "£26"]])
    t2 = table("Equipment servicing", [["1st stage", "£30*"], ["2nd stage", "£25*"], ["Stage 2 service (1st &amp; 2nd stage)", "£110"], ["Stage 3 service (1st, 2nd &amp; octo)", "£150"], ["Oxygen cleaning (1st stage)", "£8"], ["Oxygen cleaning (2nd stage)", "£7"], ["BCD", "£30*"]])
    t3 = table("Dry suit repairs (fitted)", [["Boots: socks / boots", "£191 / £223"], ["Zip: plastic / metal", "£223 / £241"], ["Neck seal: latex / neoprene", "£88 / £110"], ["Wrist seal: latex", "£96"], ["P-valve", "£306"]])
    body = page_head("", "Gas, servicing &amp; hire", "Cylinder &amp; equipment servicing", "Scuba and air rifle cylinder testing, regulator and BCD servicing, and dry suit repairs.", "kit.jpg")
    body += f'''<section class="section section--tight"><div class="wrap">{services_nav("servicing.html")}
  <div class="split__grid split__grid--top">
    <div class="prose">
      <p>We service equipment from a wide range of manufacturers through our partner dive centre. We focus on quality over quantity and take pride in our work, and our team can have you back diving in no time.</p>
      <p>Manufacturers' recommendations vary, but it's generally accepted that equipment should be serviced every 100 dives or once a year, whichever comes first. If something doesn't feel right, we'll happily give your kit a health check.</p>
      <p><a class="btn" href="contact.html?course=Servicing">Arrange a service</a></p>
    </div>
    <div class="note"><h2 class="h3">Cylinder service intervals</h2><ul class="ticks"><li>Oxygen cleaning: every 15 months</li><li>Visual inspection: every 30 months (2.5 years)</li><li>Hydrostatic test: every 60 months (5 years)</li><li>Every cylinder service includes a valve service</li></ul></div>
  </div>
  <div class="tables">{t1}{t2}{t3}</div>
  <p class="small">*Plus parts. Service kit prices vary, so contact us for the latest price.</p>
</div></section>'''
    page("servicing.html", "Cylinder & Equipment Servicing | Dive With Jimmy", "Cylinder testing, oxygen cleaning, regulator and BCD servicing and dry suit repairs in Kempston, Bedfordshire.", body, "services")


def hire():
    def t(cap, rows):
        return table(cap, rows, ["Item", "Pool", "Day", "Weekend"])
    rec = t("Recreational", [["<strong>Full recreational kit</strong>", "£30", "£70", "£120"], ["Wing / BCD", "£10", "£15", "£25"], ["Regulator", "£10", "£15", "£25"], ["Wetsuit, boots &amp; gloves", "£10", "£20", "£30"], ["Fins", "£5", "£5", "£7.50"], ["Mask &amp; snorkel", "£5", "£5", "£7.50"], ["Weights (per belt)", "Free", "£5", "£7.50"], ["Torch", "Free", "£5", "£7.50"], ["Computer", "Free", "£10", "£25"], ["DSMB &amp; reel", "£5", "£10", "£15"]])
    tec = t("Technical", [["<strong>Full technical kit (twinset)</strong>", "£40", "£70", "£125"], ["Backplate &amp; wing", "£10", "£20", "£30"], ["Twinset regulators", "£15", "£25", "£40"], ["Stage regulator", "£5", "£10", "£15"], ["Suit inflation regulator", "£5", "£10", "£15"]])
    cyl = t("Cylinders <small>(air fill included)</small>", [["Single cylinder", "£5", "£8", "£15"], ["Twinset", "£10", "£15", "£25"], ["Stage: 5.7L, 7L or 11.1L", "£5", "£10", "£15"], ["Suit inflation (1–2L)", "£3", "£5", "£10"], ["CCR set (2 or 3L)", "£10", "£15", "£25"]])
    body = page_head("", "Gas, servicing &amp; hire", "Equipment hire", "Full recreational and technical kit, from a mask to a CCR set.", "fins.jpg")
    body += f'''<section class="section section--tight"><div class="wrap">{services_nav("equipment-hire.html")}
  <div class="hire">
    <div class="hire__head"><h2 class="h3">Hire prices</h2>
      <div class="seg" role="radiogroup" aria-label="Hire period"><button role="radio" aria-checked="false" data-col="0">Pool</button><button role="radio" aria-checked="true" data-col="1">Day</button><button role="radio" aria-checked="false" data-col="2">Weekend</button></div>
    </div>
    <div class="hire__tables" data-show="1">{rec}{tec}{cyl}</div>
    <p class="small">Nitrox, oxygen, trimix and argon are charged separately; see <a href="gas-fills.html">gas fills</a>. Dive Club members get 25% off hire (excluding dry suits).</p>
  </div>
  <p><a class="btn" href="contact.html?course=Equipment+hire">Arrange your hire</a></p>
</div></section>'''
    page("equipment-hire.html", "Scuba Equipment Hire | Dive With Jimmy", "Hire recreational and technical scuba kit, cylinders and CCR sets in Kempston, Bedfordshire. Pool, day and weekend prices.", body, "services")


def expeditions():
    trips = [
        ("2027", [("HMHS Britannic", "4–13 October", "2 spaces", "photos/wreck-planes.jpg", ""),
                  ("Technical Wreck Week, Greece (45–60m)", "24–29 May · 7–12 June", "7–12 June: 2 spaces (24–29 May full)", "photos/divers-wreck.jpg", ""),
                  ("Technical Wreck Week, Greece (50–75m)", "31 May – 5 June", "Full", "photos/engine-room.jpg", "")]),
        ("2028", [("HMHS Britannic", "25 Sep – 4 Oct · 9–18 October", "2 spaces on each", "photos/wreck-planes.jpg", ""),
                  ("Farne Islands", "Dates on request", "Taking bookings", "photos/reef-sharks.jpg", "A UK favourite, often overlooked for more exotic destinations. Seals and wrecks: what more could you ask for?"),
                  ("Scapa Flow", "Dates to be confirmed", "Taking bookings", "photos/bomber.jpg", "This one needs no introduction!"),
                  ("Technical Wreck Weeks, Greece", "45–60m and 50–75m weeks", "Register interest", "photos/divers-wreck.jpg", "")]),
        ("2029", [("Jordan", "2029", "Register interest", "photos/coral-truck.jpg", ""),
                  ("Brunei", "2029", "Register interest", "photos/anemonefish.jpg", "Somewhere most people have never heard of, with wrecks at recreational and technical depths and the incredible reefs of the South China Sea. Open to recreational and technical divers.")]),
        ("2030 and beyond", [("Bikini Atoll", "25 June – 8 July 2030", "Taking bookings", "photos/aikoku.jpg", "13 nights and 19 dives aboard Pacific Master, diving the atomic wrecks of Operation Crossroads."),
                             ("Malin Head", "2030", "Register interest", "photos/sharks-wreck.jpg", ""),
                             ("Truk Lagoon", "2031", "Register interest", "photos/coral-truck.jpg", ""),
                             ("Iron Bottom Sound", "2032", "Register interest", "photos/thresher.jpg", "")])]
    secs = ""
    for yr, ts in trips:
        cards = ""
        for name, dates, status, img, txt in ts:
            full = status.lower().startswith("full")
            cards += f'''<li class="trip"><img src="assets/img/{img}" alt="" loading="lazy"><div><h3>{e(name)}</h3><p class="trip__dates">{e(dates)}</p>{f"<p>{e(txt)}</p>" if txt else ""}<p class="trip__status{" trip__status--full" if full else ""}">{e(status)}</p></div></li>'''
        secs += f'<h2 class="year">{yr}</h2><ul class="trips">{cards}</ul>'
    body = page_head("", "Explore. Dive. Discover.", "Expeditions", "Worldwide recreational and technical diving expeditions to some of the world's best destinations, with no hidden fees.", "photos/thresher.jpg")
    body += f'''<section class="section section--tight"><div class="wrap">
  <div class="split__grid split__grid--top">
    <div class="prose"><p>Our mission is to take divers beyond the ordinary, with underwater adventures that combine exploration, discovery and a shared passion for the ocean. From reefs and historic shipwrecks to challenging technical expeditions, we bring like-minded divers together in small groups with a personal approach.</p><p>Every trip is more than a diving holiday: a chance to discover new places, develop your skills, make lasting friendships and create memories that stay with you long after you've surfaced.</p></div>
    <div class="note"><h2 class="h3">Every package includes</h2><ul class="ticks"><li>Cylinder rental</li><li>Breathing gases, including helium</li><li>Sofnolime for rebreathers</li><li>Boat fees</li><li>Guiding on the dives</li><li>Our first-hand knowledge of each destination</li></ul></div>
  </div>
  {secs}
  <div class="ask__inner ask__inner--plain"><div><h2>Book your spot</h2><p>Spaces are limited. Email <a href="mailto:expeds@divewithjimmy.com">expeds@divewithjimmy.com</a> or message <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p></div><a class="btn" href="mailto:expeds@divewithjimmy.com?subject=Expedition%20enquiry">Enquire about a trip</a></div>
</div></section>'''
    page("expeditions.html", "Diving Expeditions | Dive With Jimmy", "Recreational and technical diving expeditions: HMHS Britannic, Greek technical wreck weeks, Scapa Flow, Farne Islands, Bikini Atoll and more.", body, "expeditions")


def dive_club():
    common = ["Two 90-minute pool sessions a month", "Free pool kit hire (subject to availability)", "Bring a buddy free once a month*", "25% off equipment hire (excluding dry suits; cylinders include an air fill)", "Monthly social: kit demos, film nights, dry skills practice and trip planning", "Diver development plan, reviewed twice a year", "Equipment health check twice a year"]
    def plan(name, price, extra=None):
        items = common[:4] + ([extra] if extra else []) + common[4:]
        return f'<li class="plan"><h2 class="h3">{name}</h2><p class="plan__price">£{price}<small> / month</small></p><ul class="ticks">{"".join(f"<li>{e(x)}</li>" for x in items)}</ul><a class="btn btn--block" href="https://checkout.square.site/merchant/MLTJDEN8Y67F4/checkout/3SJJM75UDYMKLAHTHTNEV7HY">Join now</a></li>'
    body = page_head("", "Dive Club", "Keep diving after your course", "A club for scuba divers, freedivers and snorkellers, with no fixed contract.", "photos/divers-wreck.jpg")
    body += f'''<section class="section section--tight"><div class="wrap">
  <ul class="plans">{plan("Snorkelling &amp; Freediving Club", 20)}{plan("Scuba Diving Club", 25, "10% off all courses (excluding trimix, tech and pro level)")}</ul>
  <p class="small">*Bring-a-buddy is limited to one visit per buddy. After their visit, they're invited to join the club.</p>
</div></section>'''
    page("dive-club.html", "Dive Club | Dive With Jimmy", "Join the Dive With Jimmy club: two pool sessions a month, 25% off hire, socials and a diver development plan. From £20 a month, no contract.", body, "club")


def about():
    body = page_head("", "About us", "Military attention to detail. A genuine love of the water.", "Founded on a passion for all things underwater, Dive With Jimmy was created to help divers reach their full potential.", "photos/aikoku.jpg")
    body += f'''<section class="section section--tight"><div class="wrap">
  <div class="people">
    <article class="person">
      <img src="assets/img/jimmy.jpg" alt="Jimmy Soos" width="853" height="570" loading="lazy">
      <div>
        <h2 class="h3">Jimmy Soos <span>Founder &amp; instructor</span></h2>
        <p>Jimmy learned to dive with the British Army in Cyprus, then kept diving through postings in the UK, Brunei and back to Cyprus. After leaving the Army he founded Dive With Jimmy to give every diver the training he wished he'd had. He loves wreck diving.</p>
        <ol class="timeline">
          <li><b>2019</b> BSAC Open Water Instructor</li>
          <li><b>Tech</b> Twinset &amp; accelerated decompression instructor; dived the Zenobia</li>
          <li><b>2022</b> Closed circuit rebreather, then CCR MOD 2</li>
          <li><b>2023</b> Cruise director on Pacific Master in Truk Lagoon and Bikini Atoll</li>
          <li><b>Today</b> Qualified to 100m on open and closed circuit</li>
        </ol>
        <a href="mailto:jimmy@divewithjimmy.com">jimmy@divewithjimmy.com</a>
      </div>
    </article>
    <article class="person">
      <img src="assets/img/emma.jpg" alt="Emma Soos underwater" width="900" height="601" loading="lazy">
      <div>
        <h2 class="h3">Emma Soos <span>Snorkel, Explorers Club &amp; Blue Oceans</span></h2>
        <p>Emma is an advocate for women in scuba diving and for looking after the ocean. She leads our SSI Snorkel Diver courses and the SSI Explorers Club, and heads up our work as an SSI Blue Oceans partner.</p>
        <a href="mailto:emma@divewithjimmy.com">emma@divewithjimmy.com</a>
      </div>
    </article>
  </div>
  <ul class="partners" aria-label="Affiliations">
    <li><img src="assets/img/ssi-partner.png" alt="SSI Official Partner: Snorkel, Freediving, Dive, Extended Range and Rebreather Center" width="600" height="110" loading="lazy"></li>
    <li><img src="assets/img/blue-oceans.png" alt="SSI Blue Oceans Official Partner" width="300" height="300" loading="lazy"></li>
    <li class="bsac"><a href="https://www.bsac.com/">BSAC<span>training centre</span></a></li>
  </ul>
</div></section>
{gallery("", "From our dives around the world")}
{contact_band("")}'''
    page("about.html", "About Us | Dive With Jimmy", "Meet Jimmy and Emma Soos. Ex-Army, qualified to 100m on open and closed circuit, and SSI Blue Oceans partners.", body, "about")


def contact():
    opts = "".join(f"<option>{e(c['n'])}</option>" for c in COURSES) + "".join(f"<option>{x}</option>" for x in ["Pool night", "Dive Club membership", "Equipment hire", "Servicing", "Gas fills", "Expeditions"])
    body = page_head("", "Get in touch", "Book a course or ask a question", "Call or message ahead before visiting, in case we're out diving.")
    body += f'''<section class="section section--tight"><div class="wrap contact__grid">
  <div>
    <ul class="details">
      <li><span>Phone</span><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
      <li><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li><span>Expeditions</span><a href="mailto:expeds@divewithjimmy.com">expeds@divewithjimmy.com</a></li>
      <li><span>Address</span><address>82 College Street<br>Kempston, Bedfordshire<br>MK42 8LU</address></li>
    </ul>
    <p><a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query=82+College+Street+Kempston+MK42+8LU">Open in Google Maps →</a></p>
    <div class="note"><h2 class="h3">Know what you want?</h2><p>Book and pay online in our shop.</p><a class="btn" href="{SHOP}">Book online</a></div>
  </div>
  <form class="form" id="enquiry" novalidate>
    <label>Your name<input name="name" autocomplete="name" required></label>
    <label>Email<input name="email" type="email" autocomplete="email" required></label>
    <label><span>Phone <small>(optional)</small></span><input name="phone" type="tel" autocomplete="tel"></label>
    <label>I'm interested in<input name="course" id="course" list="course-list" placeholder="e.g. SSI Open Water Diver"></label>
    <datalist id="course-list">{opts}</datalist>
    <label>Your message<textarea name="message" rows="5" required></textarea></label>
    <button class="btn" type="submit">Send enquiry</button>
    <p class="small form__note" role="status">This opens your email app with the message ready to send.</p>
  </form>
</div></section>'''
    page("contact.html", "Contact | Dive With Jimmy, Kempston", "Contact Dive With Jimmy: 82 College Street, Kempston, Bedfordshire MK42 8LU. Call 07538 051564 or email info@divewithjimmy.com.", body, "contact")


if __name__ == "__main__":
    home(); courses_index()
    for c in COURSES:
        course_page(c)
    whats_on(); pool_nights(); gas_fills(); servicing(); hire(); expeditions(); dive_club(); about(); contact()
    print(f"Built {len(COURSES)} course pages + 11 site pages, {len(EVENTS)} upcoming sessions in {SITE}")
