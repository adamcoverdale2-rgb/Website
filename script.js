(() => {
  document.documentElement.classList.remove('no-js');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Footer year
  document.getElementById('year').textContent = new Date().getFullYear();

  // Nav: solid background after scrolling past the top of the hero
  const nav = document.querySelector('.nav');
  const depthFill = document.querySelector('.depth__fill');
  const depthValue = document.getElementById('depth-value');
  const MAX_DEPTH = 40; // metres shown at the bottom of the page

  const onScroll = () => {
    nav.classList.toggle('is-solid', window.scrollY > 40);
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const progress = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
    depthFill.style.height = `${progress * 100}%`;
    depthValue.textContent = Math.round(progress * MAX_DEPTH);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  const toggle = document.querySelector('.nav__toggle');
  const menu = document.getElementById('nav-menu');
  const setMenu = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('is-open', open);
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });

  // Hero bubbles
  const bubbles = document.querySelector('.bubbles');
  if (bubbles && !reduceMotion) {
    for (let i = 0; i < 22; i++) {
      const b = document.createElement('span');
      const size = 4 + Math.random() * 16;
      b.className = 'bubble';
      b.style.width = b.style.height = `${size}px`;
      b.style.left = `${Math.random() * 100}%`;
      b.style.animationDuration = `${8 + Math.random() * 10}s`;
      b.style.animationDelay = `${-Math.random() * 16}s`;
      bubbles.appendChild(b);
    }
  }

  // Course tabs (WAI-ARIA tabs pattern with arrow-key support)
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const selectTab = (tab) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', (e) => {
      const step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!step) return;
      const next = tabs[(i + step + tabs.length) % tabs.length];
      selectTab(next);
      next.focus();
    });
  });

  // Team photos: hide the initials only once the photo has actually loaded
  document.querySelectorAll('.person__photo[style]').forEach((el) => {
    const url = getComputedStyle(el).getPropertyValue('--img').match(/url\(['"]?([^'")]+)/);
    if (!url) return;
    const img = new Image();
    img.onload = () => el.classList.add('img-ok');
    img.src = url[1];
  });

  // Reveal on scroll
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-in'));
  }

  // Enquiry form: validate, then open the visitor's email client with the details filled in
  const form = document.getElementById('enquiry');
  const status = form.querySelector('.form__status');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let firstInvalid = null;
    form.querySelectorAll('[required]').forEach((field) => {
      const ok = field.checkValidity() && field.value.trim() !== '';
      field.setAttribute('aria-invalid', String(!ok));
      if (!ok && !firstInvalid) firstInvalid = field;
    });
    if (firstInvalid) {
      status.textContent = 'Please add your name and a valid email address.';
      firstInvalid.focus();
      return;
    }
    const data = new FormData(form);
    const subject = `Enquiry: ${data.get('interest')}`;
    const body = [
      `Name: ${data.get('name')}`,
      `Email: ${data.get('email')}`,
      `Interested in: ${data.get('interest')}`,
      `Dates: ${data.get('dates') || 'Flexible'}`,
      '',
      data.get('message') || '',
    ].join('\n');
    window.location.href = `mailto:scuba.murcia@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    status.textContent = 'Opening your email app… If nothing happens, email scuba.murcia@outlook.com directly.';
  });
})();
