(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  // Mobile nav
  const toggle = $('.nav__toggle');
  const menu = $('#nav-menu');
  const setMenu = open => { toggle.setAttribute('aria-expanded', open); menu.classList.toggle('open', open); };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { setMenu(false); document.activeElement?.blur?.(); } });

  // Hire price period switch
  const tables = $('.hire__tables');
  if (tables) {
    const seg = $$('.hire .seg button');
    seg.forEach(b => b.addEventListener('click', () => {
      seg.forEach(x => x.setAttribute('aria-checked', x === b));
      tables.dataset.show = b.dataset.col;
    }));
  }

  // Courses page: search + agency filter
  const search = $('#course-search');
  if (search) {
    let agency = 'all';
    const cards = $$('.ccard');
    const cats = $$('.cat');
    const empty = $('.empty');
    const apply = () => {
      const q = search.value.trim().toLowerCase();
      cards.forEach(c => {
        c.hidden = !((agency === 'all' || c.dataset.agency === agency) && (!q || c.dataset.name.includes(q) || c.textContent.toLowerCase().includes(q)));
      });
      let any = false;
      cats.forEach(s => { const vis = $$('.ccard', s).some(c => !c.hidden); s.hidden = !vis; any ||= vis; });
      empty.hidden = any;
    };
    search.addEventListener('input', apply);
    const seg = $$('.filter .seg button');
    seg.forEach(b => b.addEventListener('click', () => {
      seg.forEach(x => x.setAttribute('aria-checked', x === b));
      agency = b.dataset.agency; apply();
    }));
  }

  // Contact form: prefill course from ?course=, then open the visitor's email app
  const form = $('#enquiry');
  if (form) {
    const course = new URLSearchParams(location.search).get('course');
    if (course) $('#course').value = course;
    form.addEventListener('submit', e => {
      e.preventDefault();
      let ok = true;
      $$('[required]', form).forEach(f => {
        const bad = !f.value.trim() || (f.type === 'email' && !f.checkValidity());
        f.setAttribute('aria-invalid', bad);
        if (bad && ok) { f.focus(); ok = false; }
      });
      const note = $('.form__note', form);
      if (!ok) { note.textContent = 'Please fill in your name, a valid email and a message.'; return; }
      const d = Object.fromEntries(new FormData(form));
      const subject = `Enquiry${d.course ? ': ' + d.course : ''} from ${d.name}`;
      const body = `${d.message}\n\nName: ${d.name}\nEmail: ${d.email}${d.phone ? '\nPhone: ' + d.phone : ''}${d.course ? '\nInterested in: ' + d.course : ''}`;
      location.href = `mailto:info@divewithjimmy.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      note.textContent = 'Your email app should open now. If it doesn\'t, email info@divewithjimmy.com.';
    });
  }

  // Scroll reveal
  const els = $$('.head, .tile, .person, .ticket, .note, .plan, .trip, .about-teaser > *');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    els.forEach(el => { el.classList.add('reveal'); io.observe(el); });
  }

  const yr = $('.footer .yr'); if (yr) yr.textContent = new Date().getFullYear();
})();
