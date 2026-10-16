/* ==========================================================================
   Roopashree — portfolio behaviour
   Small, dependency-free. Everything here is an enhancement: the page is fully
   readable and navigable with this file absent.
   ========================================================================== */

(function () {
  'use strict';

  var root = document.documentElement;
  var STORAGE_KEY = 'rs-theme';

  /* ------------------------------------------------------------------ theme
     The button label always states the mode you would switch TO, so it reads
     correctly without an icon. */
  function applyTheme(theme) {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;

    var next = theme === 'light' ? 'dark' : 'light';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.textContent = next === 'light' ? 'Light mode' : 'Dark mode';
      btn.setAttribute('aria-label', 'Switch to ' + next + ' theme');
      btn.setAttribute('aria-pressed', String(theme === 'light'));
    });
  }

  function currentTheme() {
    return root.dataset.theme === 'light' ? 'light' : 'dark';
  }

  applyTheme(currentTheme());

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'light' ? 'dark' : 'light';
      applyTheme(next);
      try { localStorage.setItem(STORAGE_KEY, next); } catch (e) { /* storage blocked */ }
    });
  });

  /* --------------------------------------------------------------- mobile nav */
  var toggle = document.querySelector('.nav__toggle');
  var menu = document.getElementById('nav-menu');

  function setMenu(open) {
    if (!menu || !toggle) return;
    menu.dataset.open = String(open);
    toggle.setAttribute('aria-expanded', String(open));
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      setMenu(menu.dataset.open !== 'true');
    });

    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) setMenu(false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') setMenu(false);
    });
  }

  /* --------------------------------------------------- active section marker */
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav__list a[href^="#"]'));
  var sections = links
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) {
          var isCurrent = a.getAttribute('href') === '#' + entry.target.id;
          if (isCurrent) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    sections.forEach(function (section) { observer.observe(section); });
  }

  /* ------------------------------------------------------------------- year */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
