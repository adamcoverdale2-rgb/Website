(() => {
  // Mobile nav
  const toggle = document.querySelector('.nav__toggle');
  const menu = document.getElementById('nav-menu');
  const setMenu = open => { toggle.setAttribute('aria-expanded', open); menu.classList.toggle('open', open); };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

  // Course tabs (arrow keys move between tabs)
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const select = tab => {
    tabs.forEach(t => {
      const on = t === tab;
      t.setAttribute('aria-selected', on);
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', e => {
      const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!d) return;
      const next = tabs[(i + d + tabs.length) % tabs.length];
      select(next); next.focus();
    });
  });

  // Hire price period switch
  const tables = document.querySelector('.hire__tables');
  const seg = [...document.querySelectorAll('.seg button')];
  seg.forEach(b => b.addEventListener('click', () => {
    seg.forEach(x => x.setAttribute('aria-checked', x === b));
    tables.dataset.show = b.dataset.col;
  }));

  // "Enquire" links prefill the course field
  const course = document.getElementById('course');
  const list = document.getElementById('course-list');
  const names = new Set();
  document.querySelectorAll('[data-course]').forEach(a => {
    names.add(a.dataset.course);
    a.addEventListener('click', () => { course.value = a.dataset.course; });
  });
  names.forEach(n => list.append(new Option(n)));

  // Enquiry form: opens the visitor's email app with the details filled in
  const form = document.getElementById('enquiry');
  form.addEventListener('submit', e => {
    e.preventDefault();
    let ok = true;
    form.querySelectorAll('[required]').forEach(f => {
      const bad = !f.value.trim() || (f.type === 'email' && !f.checkValidity());
      f.setAttribute('aria-invalid', bad);
      if (bad && ok) { f.focus(); ok = false; }
    });
    const note = form.querySelector('.form__note');
    if (!ok) { note.textContent = 'Please fill in your name, a valid email and a message.'; return; }
    const d = Object.fromEntries(new FormData(form));
    const subject = `Enquiry${d.course ? ': ' + d.course : ''} from ${d.name}`;
    const body = `${d.message}\n\nName: ${d.name}\nEmail: ${d.email}${d.phone ? '\nPhone: ' + d.phone : ''}${d.course ? '\nInterested in: ' + d.course : ''}`;
    location.href = `mailto:info@divewithjimmy.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    note.textContent = 'Your email app should open now. If it doesn\'t, email info@divewithjimmy.com.';
  });

  // Scroll reveal
  const els = document.querySelectorAll('.head, .feature, .card, .services li, .person, .ticket, .hire, .form');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    els.forEach(el => { el.classList.add('reveal'); io.observe(el); });
  }

  document.getElementById('year').textContent = new Date().getFullYear();
})();
